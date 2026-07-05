# Specification: Server-Side Proxy Routing & IAM Authentication
## Project: Agent for Good - Secure Application Proxy Layer

## Objective
To define the server-side architecture, proxy routing mechanics, and Google IAM OpenID Connect (OIDC) identity injection for the backend server layer. This private proxy shields the Python Inference API from public traffic, intercepts requests from the IAP-protected frontend, and signs downstream requests using an authorized Service Principal.

---

### Architectural Role & Security Topology
The server-side route operates entirely behind Google Cloud Identity-Aware Proxy (IAP). It acts as an isolated network bridge:
* **Inbound Traffic:** Accepts local, trusted requests from the React application context after Google IAP has fully authenticated the user's identity.
* **Outbound Traffic:** Dynamically fetches a cryptographically signed Google OIDC ID token matching the identity of a designated Service Account. It appends this token to the downstream call, satisfying the private Python Function's `--no-allow-unauthenticated` IAM configuration.

---

### Runtime Environment & Core Dependencies
The proxy layer is integrated into the application's runtime server configuration using the following primary Node.js/TypeScript modules:
* **`google-auth-library`**: Used to interface with the ambient Google Cloud IAM subsystem, fetch internal metadata, and generate signed identity tokens target audience paths.
* **Server Framework Web Dependencies**: Standard route handlers (`express` and `cors`) to construct the listener context and parse payload vectors.

---

### Server Route Configuration (`/api/evaluate-risk`)
The server exposes a secure HTTP POST endpoint that wraps the data-payload mapping and tokens injection loop cleanly:

#### Target Mapping Parameters
* **Method:** `POST`
* **Route Path:** `/api/evaluate-risk`
* **Target Downstream Destination:** Cloud Function endpoint URL derived dynamically from environment flags.

#### Algorithmic Execution Workflow
1. **Payload Extraction:** Intercept the arriving JSON object containing the 16 heart disease lifestyle and clinical features from the client UI.
2. **Identity Header Assertion (Optional Audit):** Validate that IAP identity headers (`x-goog-authenticated-user-email`) are bound to the incoming stream for auditing purposes.
3. **IAM Token Generation:** Invoke the Google Auth library to generate a fresh target OpenID Connect (OIDC) ID token. The token's **audience** parameter must explicitly target the underlying Python Cloud Function URL.
4. **Header Injection:** Construct a clean outbound HTTP configuration containing an `Authorization` payload mapped as `Bearer <GCP_OIDC_ID_TOKEN>`.
5. **Downstream Dispatch:** Post the clean payload to the private Python endpoint.
6. **Response Transformation:** Receive the calculated metrics (`raw_probability`, `risk_category`) from the model execution loop and relay them back to the React UI as a standardized JSON structure.

---

### Technical Blueprint Pipeline Mechanics
To guarantee robust asynchronous execution without embedding static programming assets, the interface lifecycle must implement the following structural validation criteria:

* **Target URL Validation Verification:** Prior to fetching tokens, the system asserts that the downstream environment variable (`INFERENCE_API_URL`) is populated. If empty, it fails fast with an HTTP `500 Internal Server Error` to prevent silent routing black holes.
* **Ambient Credentials Extraction:** The routing layer utilizes implicit application default credentials (ADC) bound to the hosting cloud compute runtime rather than relying on external, hardcoded service key files.
* **Token Lifetime Containment:** The generated OpenID Connect identity token must match the exact target cloud function base address as its declared cryptographic audience string.
* **Error Interception Matrix:** If the communication to the Python backend breaks down, the route captures the error payload details, strips out internal system stack traces, and sends a sanitized, secure error envelope back to the interface client.

