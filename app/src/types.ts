// Define acceptable literal types based on CDC/UCI requirements
export type SexType = "Male" | "Female" | "";
export type AgeCategoryType =
  | "18-24"
  | "25-29"
  | "30-34"
  | "35-39"
  | "40-44"
  | "45-49"
  | "50-54"
  | "55-59"
  | "60-64"
  | "65-69"
  | "70-74"
  | "75-79"
  | "80 or older"
  | "";
export type YesNoType = "Yes" | "No" | "";
export type DiabeticType =
  | "Yes"
  | "No"
  | "No, borderline diabetes"
  | "Yes (during pregnancy)"
  | "";
export type GenHealthType =
  | "Excellent"
  | "Very good"
  | "Good"
  | "Fair"
  | "Poor"
  | "";

// Core state schema for the collected patient features
export interface HeartDiseaseFormData {
  sex: SexType;
  age_category: AgeCategoryType;
  bmi: number | null;
  smoking: YesNoType;
  alcohol_drinking: YesNoType;
  stroke: YesNoType;
  diabetic: DiabeticType;
  physical_activity: YesNoType;
  gen_health: GenHealthType;
  diff_walking: YesNoType;
  asthma: YesNoType;
  kidney_disease: YesNoType;
  skin_cancer: YesNoType;
  physical_health: number | null;
  mental_health: number | null;
  sleep_time: number | null;
}

// Application State Machine Tiers
export type AppStepState =
  | "WELCOME"
  | "QUESTIONING"
  | "READY_TO_SUBMIT"
  | "PROCESSING"
  | "RESULTS";

// Structural Question Definition Mapping
export interface QuestionDefinition {
  key: keyof HeartDiseaseFormData;
  label: string;
  type: "select" | "text" | "number" | "bmi_calculator";
  options?: string[];
  validation: (value: any) => boolean;
}

// Agent UI State pushed by the Data Agent
export interface AgentUIState {
  currentQuestionText: string;
  targetFeatureKey: keyof HeartDiseaseFormData;
  expectedInputType: "text" | "number" | "select" | "bmi_calculator";
  selectOptions?: string[];
  isFirstQuestion: boolean;
  isLastQuestion: boolean;
}
