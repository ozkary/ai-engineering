Swapping eventSourceInit.headers for requestInit.headers solves half the problem by fixing the outbound payload headers, but it introduces a major breaking change for the initial connection phase. By removing your token from eventSourceInit, the initial GET request that sets up the event stream is now hitting Google Identity-Aware Proxy (IAP) completely unauthenticated, resulting in the 403 Forbidden error. 

## The Core Issues 
- request Init only targets POSTs: In the official @modelcontextprotocol/sdk, options inside requestInit are applied strictly to the fetch POST requests. The initial connection relies on eventSourceInit.
- Native EventSource Header Limitations: Native browser EventSource implementations do not accept a headers object. If your MCP client is running in a Node.js context, the underlying polyfill package does support a custom fetch parameter inside eventSourceInit to handle headers dynamically.
- IAP Audience Requirements: Unlike a standard Cloud Run service-to-service call where the audience (aud) claim is the Cloud Run URL, an IAP-protected application requires the audience to match the IAP OAuth Client ID.
  > [!IMPORTANT]
  > **Note for Downstream APIs**: In this architecture, while the frontend (`heart-disease-risk-ui`) is protected by IAP, the downstream Python API (`heart-disease-risk-assessment`) is a private Cloud Run service protected by standard **Google Cloud IAM (Cloud Run Invoker)**. Thus, for the frontend-to-API communication, the OIDC token audience must remain the **Cloud Run service URL**, not the IAP Client ID.

# How to Properly Fix the SDK Initialization

To pass the OIDC service account token to both the stream setup (IAP / EventSource) and the message payload handlers (fetch), you must configure both blocks inside the SSEClientTransport constructor using a custom fetch wrapper. 

```typescript
const transport = new SSEClientTransport(targetUrl, {
  // 1. Controls the POST requests (/message endpoint)
  requestInit: {
    headers: {
      "Authorization": `Bearer ${oidcToken}`,
    },
  },
  // 2. Controls the initial GET request (EventSource connection through IAP)
  eventSourceInit: {
    // The underlying Node event source package allows a custom fetch override
    fetch: (input, init) => {
      const headers = new Headers(init?.headers);
      headers.set("Authorization", `Bearer ${oidcToken}`);
      
      return fetch(input, {
        ...init,
        headers,
      });
    },
  },
});
```

### Cloud Run & IAP Requirements Checklist

If you update the code and still hit a 403, verify these Google Cloud settings:

- Audience Claim Validation: Ensure the OIDC token was generated with the target audience (aud) configured to the IAP OAuth Client ID, not the Cloud Run endpoint URL. You can find this client id in the Google Cloud Console under Security > Identity-Aware Proxy.
- IAM Roles: The service account generating the token must be assigned the IAP-secured Web App User (roles/iap.httpsResourceAccessor) role on the IAP resource.
- HTTP/2 Configurations: SSE connections require persistent, unbuffered transport. If you notice streaming data arriving delayed or batched, ensure HTTP/2 is enabled on your Cloud Run service configuration.

## Correct Nodejs app

To fix the 403 Forbidden error in your Node.js server, you must ensure that your generated OIDC token targets the IAP OAuth Client ID (not the Cloud Run URL), and that you inject this token into both the stream connection and the POST requests using a Node.js-compatible fetch override.Here is the complete, working implementation using the official @google-cloud/local-auth or google-auth-library along with the @modelcontextprotocol/sdk.

### Programmatically Generate the Correct Token

When calling an application behind Identity-Aware Proxy (IAP), your Service Account must generate an OIDC token where the audience (aud) is the IAP Client ID

```typescript
import { GoogleAuth } from 'google-auth-library';

// Replace with your actual IAP Client ID from the GCP Console
// Format looks like: ://googleusercontent.com
const IAP_CLIENT_ID = "YOUR_IAP_OAUTH_CLIENT_ID"; 
const CLOUD_RUN_URL = "https://run.app";

async function getIapToken() {
  const auth = new GoogleAuth();
  const client = await auth.getIdTokenClient(IAP_CLIENT_ID);
  
  // This automatically fetches or refreshes the OIDC token for the IAP audience
  const res = await client.getRequestHeaders(); 
  return res.Authorization; // Returns "Bearer <token>"
}

```

### 2. Configure the MCP SSEClientTransport in Node.js

Because Node.js does not have the native browser limitations of EventSource, the MCP SDK uses an underlying Node polyfill that accepts a custom fetch function inside eventSourceInit. This setup applies your IAP token to both the initial stream initialization and the subsequent message payloads:

```typescript
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

async function initializeMcpClient() {
  const authorizationHeader = await getIapToken(); // "Bearer <token>"

  const transport = new SSEClientTransport(new URL(CLOUD_RUN_URL), {
    // Phase 1: Authentication for POST requests (/message)
    requestInit: {
      headers: {
        "Authorization": authorizationHeader,
      },
    },
    // Phase 2: Authentication for the initial GET request (EventSource)
    eventSourceInit: {
      fetch: (input, init) => {
        const headers = new Headers(init?.headers);
        headers.set("Authorization", authorizationHeader);
        
        return fetch(input, {
          ...init,
          headers,
        });
      },
    },
  });

  return transport;
}


```

### Verify Your Python (Cloud Run) Configuration

If the Node.js server passes the token correctly but the Python backend still throws a 403, check these settings:

- Buffering Issues: Python framework servers (like FastAPI, Flask, or Quart) often buffer responses by default. For SSE to work smoothly over Cloud Run, ensure your Python code yields events immediately and sets the response headers to X-Accel-Buffering: no.
- IAM Permission Check: Ensure that the Service Account identity used by your Node.js application has the IAP-secured Web App User (roles/iap.httpsResourceAccessor) role bound to it in the Google Cloud Console under Security > Identity-Aware Proxy.