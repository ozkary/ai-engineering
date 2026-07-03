import { LlmAgent, Gemini } from "@google/adk";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { GoogleAuth } from "google-auth-library";
import { EventSource } from "eventsource";
import { HeartDiseaseFormData } from "../../../src/types";

// Polyfill EventSource for Model Context Protocol SSE client transport
(global as any).EventSource = EventSource;

const auth = new GoogleAuth();

/**
 * Generates the Google OIDC ID token to pass through the Cloud Function's IAM firewall.
 */
async function getOidcToken(audience: string): Promise<string | undefined> {
  try {
    const client = await auth.getIdTokenClient(audience);
    const headers = await client.getRequestHeaders();
    return headers["Authorization"];
  } catch (error) {
    console.warn("Could not generate Google OIDC token (perhaps running locally):", error);
    return undefined;
  }
}

/**
 * MCP client evaluation tool executor
 */
export async function callInferenceMCP(
  data: HeartDiseaseFormData,
  inferenceApiUrl: string
): Promise<{ raw_probability: number; risk_category: string }> {
  const token = await getOidcToken(inferenceApiUrl);

  const transport = new SSEClientTransport(new URL(inferenceApiUrl), {
    eventSourceInit: {
      headers: token ? { Authorization: token } : undefined,
    },
  });

  const client = new Client(
    {
      name: "hd-analysis-agent-client",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  try {
    await client.connect(transport);
    const response = await client.callTool({
      name: "evaluate_heart_risk",
      arguments: {
        features: data,
      },
    });

    if (!response || !response.content || response.content.length === 0) {
      throw new Error("Empty response received from MCP evaluate_heart_risk tool");
    }

    const textContent = response.content[0];
    if (textContent.type !== "text") {
      throw new Error("Unexpected content type received from MCP tool");
    }

    try {
      return JSON.parse(textContent.text);
    } catch (parseError) {
      throw new Error(`Inference Service Error: ${textContent.text}`);
    }
  } finally {
    await transport.close();
  }
}

import fs from "fs";
import path from "path";

// Load risk review prompt
let riskReviewInstruction =
  "Role Configuration: Senior Cardio respiratory Data Analyst & Health Coach.\n" +
  "Constraints:\n" +
  "- You must communicate objective, professional, and clear risk interpretations.\n" +
  "- You must directly trace risks back to specific input feature pairings (e.g., matching a high risk score to a combination of smoking history and low sleep times).\n" +
  "- Rely on factual statistics, avoid diagnostic statements, and focus on lifestyle advice.";

try {
  const promptPath = process.env.RISK_REVIEW_PROMPT_PATH || "./server/prompts/risk-review.md";
  const resolvedPath = path.resolve(promptPath);
  if (fs.existsSync(resolvedPath)) {
    riskReviewInstruction = fs.readFileSync(resolvedPath, "utf-8");
  } else {
    console.warn(`Warning: Prompt file not found at ${resolvedPath}. Using hardcoded fallback.`);
  }
} catch (error) {
  console.error("Error reading prompt file, using fallback:", error);
}

/**
 * Agent Definition: llm_risk_review LlmAgent instance.
 * Employs native Gemini model configurations and instructions.
 */
export const llm_risk_review = new LlmAgent({
  name: "llm_risk_review",
  model: new Gemini({
    model: process.env.GEMINI_MODEL || "gemini-2.5-flash",
    vertexai: true,
    project: process.env.GCP_PROJECT_ID,
    location: process.env.GCP_LOCATION || "us-east1",
  }),
  instruction: riskReviewInstruction,
});
