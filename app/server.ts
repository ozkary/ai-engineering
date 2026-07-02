import express from "express";
import cors from "cors";
import { GoogleAuth } from "google-auth-library";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const PORT = process.env.PORT || 3001;
const INFERENCE_API_URL = process.env.INFERENCE_API_URL;

app.use(cors());
app.use(express.json());

// Initialize Google Auth client
const auth = new GoogleAuth();

app.post("/api/evaluate-risk", async (req, res) => {
  if (!INFERENCE_API_URL) {
    console.error("Configuration Error: INFERENCE_API_URL env variable is not set.");
    return res.status(500).json({
      status: "error",
      message: "Internal Server Configuration Error: Target inference URL is missing."
    });
  }

  try {
    // 1. Generate Google OIDC ID Token with the target URL as the audience
    console.log(`Generating Google OIDC token for audience: ${INFERENCE_API_URL}`);
    const client = await auth.getIdTokenClient(INFERENCE_API_URL);
    const headers = await client.getRequestHeaders();
    const token = headers["Authorization"]; // Returns "Bearer <token>"

    if (!token) {
      throw new Error("Failed to retrieve Google IAM OIDC token.");
    }

    // 2. Dispatch request to the private Python inference backend
    console.log(`Forwarding payload to inference API at ${INFERENCE_API_URL}`);
    const apiResponse = await fetch(INFERENCE_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token,
      },
      body: JSON.stringify(req.body),
    });

    const data = await apiResponse.json();

    if (!apiResponse.ok) {
      console.error("Downstream API returned error status:", apiResponse.status, data);
      return res.status(apiResponse.status).json({
        status: "error",
        message: data.message || "Failed to process downstream risk assessment."
      });
    }

    // 3. Return mapped results to client
    return res.status(200).json(data);

  } catch (error: any) {
    console.error("Proxy Service Exception:", error);
    return res.status(500).json({
      status: "error",
      message: "An internal proxy exception occurred while communicating with the inference pipeline."
    });
  }
});

// Production: Serve the React static build folder
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distPath = path.join(__dirname, "dist");

// Serve static files if they exist
app.use(express.static(distPath));

// Fallback all other routes to React SPA
app.get("*", (req, res) => {
  res.sendFile(path.join(distPath, "index.html"));
});

app.listen(PORT, () => {
  console.log(`Secure application proxy listening on port ${PORT}`);
  console.log(`Target inference API: ${INFERENCE_API_URL || "NOT SET"}`);
});
