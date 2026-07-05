import { InMemoryRunner } from "@google/adk";
import { HeartDiseaseFormData } from "../../../src/types";

export const MANDATORY_DISCLOSURE = 
  "DISCLAIMER: This analysis is an advanced statistical calculation based on machine learning weights and does not replace professional medical diagnosis, treatment, or advice.";

/**
 * Pre-Execution Guardrail
 * Inspects incoming clinical and lifestyle inputs before tool dispatching to reject anomalous values.
 */
export function validateHeartRiskPayload(data: Partial<HeartDiseaseFormData>): { isValid: boolean; error?: string } {
  const requiredKeys: (keyof HeartDiseaseFormData)[] = [
    "sex", "age_category", "bmi", "smoking", "alcohol_drinking", "stroke", 
    "diabetic", "physical_activity", "gen_health", "diff_walking", "asthma", 
    "kidney_disease", "skin_cancer", "physical_health", "mental_health", "sleep_time"
  ];

  for (const key of requiredKeys) {
    if (data[key] === undefined || data[key] === null || data[key] === "") {
      return { isValid: false, error: `Missing required field: ${key}` };
    }
  }

  // Sane bounds checking
  if (data.bmi !== null && (data.bmi < 10 || data.bmi > 100)) {
    return { isValid: false, error: `Anomalous BMI value: ${data.bmi}. Must be between 10 and 100.` };
  }

  if (data.physical_health !== null && (data.physical_health < 0 || data.physical_health > 30)) {
    return { isValid: false, error: `Anomalous physical_health value: ${data.physical_health}. Must be between 0 and 30.` };
  }

  if (data.mental_health !== null && (data.mental_health < 0 || data.mental_health > 30)) {
    return { isValid: false, error: `Anomalous mental_health value: ${data.mental_health}. Must be between 0 and 30.` };
  }

  if (data.sleep_time !== null && (data.sleep_time < 0 || data.sleep_time > 24)) {
    return { isValid: false, error: `Anomalous sleep_time value: ${data.sleep_time}. Must be between 0 and 24.` };
  }

  return { isValid: true };
}

/**
 * ADK Compute Runnets Orchestration
 * Exposes a clean runner invocation wrapper protecting state boundaries between async requests.
 */
export async function executeWorkflowRunner(agent: any, payload: any): Promise<any> {
  const runner = new InMemoryRunner({
    appName: "HeartRiskGovernanceRunner",
    agent: agent,
  });

  let finalResult: any = null;
  const runGen = runner.runEphemeral({
    userId: "system-user",
    newMessage: {
      role: "user",
      parts: [{ text: JSON.stringify(payload) }],
    },
  });

  for await (const event of runGen) {
    if (event.content?.parts?.[0]?.text) {
      try {
        finalResult = JSON.parse(event.content.parts[0].text);
      } catch {
        finalResult = event.content.parts[0].text;
      }
    }
  }

  if (!finalResult) {
    throw new Error("ADK Runner execution failed to return a valid result.");
  }

  return finalResult;
}
