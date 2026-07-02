import { BaseAgent, InvocationContext, Event, createEvent } from "@google/adk";
import { validateHeartRiskPayload, MANDATORY_DISCLOSURE } from "../governance/compliance";
import { callInferenceMCP, llm_risk_review } from "../agents/analystAgent";

// Workflow Edge Transition Constants
export const START = "START";
export const parse_request = "parse_request";
export const send_mcp_request = "send_mcp_request";
export const llm_risk_review_node = "llm_risk_review";
export const send_analysis = "send_analysis";

export interface WorkflowConfig {
  name: string;
  edges: [string, string][];
}

/**
 * Custom Workflow BaseAgent implementation that maps transition edges to execution nodes.
 * This guarantees execution order and state-graph compliance.
 */
export class WorkflowAgent extends BaseAgent {
  private config: WorkflowConfig;

  constructor(config: WorkflowConfig) {
    super({
      name: config.name,
      description: "State graph workflow orchestrator mapping transition edges to execution nodes.",
    });
    this.config = config;
  }

  protected async *runAsyncImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
    const payloadStr = context.userContent?.parts?.[0]?.text;
    if (!payloadStr) {
      throw new Error("Workflow Execution Error: Missing payload string.");
    }

    const payload = JSON.parse(payloadStr);
    let mcpResult: any = null;
    let reviewText = "";

    // Track state graph transitions via configured edges
    for (const [from, to] of this.config.edges) {
      console.log(`[Workflow Transition] ${from} -> ${to}`);

      switch (to) {
        case parse_request: {
          const validation = validateHeartRiskPayload(payload);
          if (!validation.isValid) {
            throw new Error(`Payload validation failed in parse_request: ${validation.error}`);
          }
          break;
        }

        case send_mcp_request: {
          const inferenceUrl = process.env.INFERENCE_API_URL;
          if (!inferenceUrl) {
            throw new Error("Configuration Error: INFERENCE_API_URL is missing.");
          }
          mcpResult = await callInferenceMCP(payload, inferenceUrl);
          break;
        }

        case llm_risk_review_node: {
          // Construct rich context for the LLM risk review agent
          const prompt = `
Patient Profile:
${JSON.stringify(payload, null, 2)}

Model Prediction Metrics:
- Raw Probability: ${(mcpResult.raw_probability * 100).toFixed(2)}%
- Risk Category: ${mcpResult.risk_category}
`;

          // Inject user prompt context into session events history
          context.session.events.push(
            createEvent({
              invocationId: context.invocationId,
              author: "user",
              content: {
                role: "user",
                parts: [{ text: prompt }],
              },
            })
          );

          // Execute the imported llm_risk_review ADK agent
          for await (const event of llm_risk_review.runAsync(context)) {
            if (event.content?.parts?.[0]?.text) {
              reviewText += event.content.parts[0].text;
            }
          }
          break;
        }

        case send_analysis: {
          const finalResponse = {
            status: "success",
            raw_probability: mcpResult.raw_probability,
            risk_category: mcpResult.risk_category,
            analysis: reviewText || "Unable to produce risk review narrative.",
            disclosure: MANDATORY_DISCLOSURE,
          };

          yield createEvent({
            invocationId: context.invocationId,
            content: {
              role: "model",
              parts: [{ text: JSON.stringify(finalResponse) }],
            },
          });
          break;
        }
      }
    }
  }

  protected async *runLiveImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
    throw new Error("Live execution is not supported.");
  }
}

/**
 * Helper to build the ADK state-graph Workflow agent according to the spec's blueprint.
 */
export function Workflow(config: WorkflowConfig): WorkflowAgent {
  return new WorkflowAgent(config);
}

/**
 * Linear state graph blueprint declaration.
 */
export const root_agent = Workflow({
  name: "hd_analysis_agent",
  edges: [
    [START, parse_request],
    [parse_request, send_mcp_request],
    [send_mcp_request, llm_risk_review_node],
    [llm_risk_review_node, send_analysis],
  ],
});
