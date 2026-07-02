from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from a2wsgi import ASGIMiddleware
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from predict import HeartDiseaseFeatures, prepare_input, predict, probability_label

# 1. Initialize FastMCP
mcp = FastMCP("Heart Disease Risk Assessment MCP Server")

# Register evaluate_heart_risk tool
@mcp.tool(
    name="evaluate_heart_risk",
    description="Evaluates a patient's 16-feature lifestyle/demographic matrix and returns a localized XGBoost statistical risk classification."
)
def evaluate_heart_risk(features: HeartDiseaseFeatures) -> dict:
    input_data = prepare_input(features)
    raw_prob = predict(input_data)
    category = probability_label(raw_prob)
    return {
        "status": "success",
        "raw_probability": raw_prob,
        "risk_category": category
    }

# 2. Setup SSE Transport
transport = SseServerTransport("/messages")

async def handle_sse(request):
    async with transport.connect_sse(request.scope, request.receive, request._send) as (in_stream, out_stream):
        await mcp._mcp_server.run(
            in_stream,
            out_stream,
            mcp._mcp_server.create_initialization_options()
        )
    return Response()

# 3. Predict Endpoint for standard POST ingestion
async def predict_risk_endpoint(request):
    # Identity Verification: Assert presence of GCP IAM OIDC token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JSONResponse({"status": "error", "message": "Missing or invalid Authorization header"}, status_code=401)

    id_token = auth_header.split('Bearer ')[1]
    if not id_token or len(id_token.strip()) < 10:
        return JSONResponse({"status": "error", "message": "Unauthorized: Invalid token format"}, status_code=401)

    # Payload Ingestion & Validation
    try:
        request_json = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "message": "Missing or invalid JSON request body"}, status_code=400)

    try:
        features = HeartDiseaseFeatures(**request_json)
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Invalid input parameters: {str(e)}"}, status_code=400)

    # Inference and Label Mapping
    try:
        input_data = prepare_input(features)
        raw_prob = predict(input_data)
        category = probability_label(raw_prob)

        return JSONResponse({
            "status": "success",
            "raw_probability": raw_prob,
            "risk_category": category
        }, status_code=200)
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Inference pipeline execution error: {str(e)}"}, status_code=500)

# Build Routes
routes = [
    Route("/sse", handle_sse, methods=["GET"]),
    Mount("/messages", app=transport.handle_post_message),
    Route("/", predict_risk_endpoint, methods=["POST"])
]

# Configure ASGI Application
app = Starlette(
    routes=routes,
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    ]
)

# Export WSGI Middleware adapter for Google Cloud Functions
predict_risk_main = ASGIMiddleware(app)
