import express from "express";
import cors from "cors";
import { GoogleAuth } from "google-auth-library";
import path from "path";
import { fileURLToPath } from "url";
import { root_agent } from "./server/src/workflows/heartRiskWorkflow";
import { executeWorkflowRunner } from "./server/src/governance/compliance";

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
    console.log("Triggering server-side ADK Workflow & Agent Governance...");
    const result = await executeWorkflowRunner(root_agent, req.body);
    return res.status(200).json(result);
  } catch (error: any) {
    console.error("Proxy Service Exception:", error);
    return res.status(500).json({
      status: "error",
      message: error.message || "An error occurred while executing the heart risk agent workflow."
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
