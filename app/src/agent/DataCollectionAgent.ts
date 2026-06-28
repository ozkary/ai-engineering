import type {
  AgentUIState,
  HeartDiseaseFormData,
  QuestionDefinition,
} from "../types";
import { AgentBase } from "./AgentBase";
import questionsJson from "./data-agent.json";

interface QuestionMetadata {
  key: string;
  label: string;
  type: "select" | "text" | "number" | "bmi_calculator";
  options?: string[];
  validationRange?: {
    min: number;
    max: number;
    isFloat: boolean;
  };
}

export class DataCollectionAgent extends AgentBase {
  private questions: QuestionDefinition[];
  private currentIndex = 0;
  private formData: HeartDiseaseFormData = {
    sex: "",
    age_category: "",
    bmi: null,
    smoking: "",
    alcohol_drinking: "",
    stroke: "",
    diabetic: "",
    physical_activity: "",
    gen_health: "",
    diff_walking: "",
    asthma: "",
    kidney_disease: "",
    skin_cancer: "",
    physical_health: null,
    mental_health: null,
    sleep_time: null,
  };

  constructor() {
    super("DataCollectionAgent");

    // Dynamically compile the question validation functions from metadata json
    const metaList = questionsJson as QuestionMetadata[];
    this.questions = metaList.map((item) => {
      let validationFn: (value: any) => boolean;

      if (item.type === "select" && item.options) {
        validationFn = (val: any) => item.options!.includes(val);
      } else if (
        (item.type === "number" || item.type === "bmi_calculator") &&
        item.validationRange
      ) {
        const range = item.validationRange;
        validationFn = (val: any) => {
          const num = range.isFloat
            ? Number.parseFloat(val)
            : Number.parseInt(val, 10);
          return !Number.isNaN(num) && num >= range.min && num <= range.max;
        };
      } else {
        // Fallback validation
        validationFn = (val: any) => val !== undefined && val !== "";
      }

      return {
        key: item.key as keyof HeartDiseaseFormData,
        label: item.label,
        type: item.type,
        options: item.options,
        validation: validationFn,
      };
    });
  }

  public getQuestions(): QuestionDefinition[] {
    return this.questions;
  }

  public getCurrentIndex(): number {
    return this.currentIndex;
  }

  public jumpToQuestion(key: keyof HeartDiseaseFormData): AgentUIState {
    const idx = this.questions.findIndex((q) => q.key === key);
    if (idx !== -1) {
      this.currentIndex = idx;
      this.log(
        `Direct navigation jump to key ${key}. Index is now ${this.currentIndex}.`,
      );
    }
    return this.getUIState();
  }

  public getFormData(): HeartDiseaseFormData {
    return { ...this.formData };
  }

  public getUIState(): AgentUIState {
    const q = this.questions[this.currentIndex];
    return {
      currentQuestionText: q.label,
      targetFeatureKey: q.key,
      expectedInputType: q.type,
      selectOptions: q.options,
      isFirstQuestion: this.currentIndex === 0,
      isLastQuestion: this.currentIndex === this.questions.length - 1,
    };
  }

  public start(): AgentUIState {
    this.currentIndex = 0;
    this.formData = {
      sex: "",
      age_category: "",
      bmi: null,
      smoking: "",
      alcohol_drinking: "",
      stroke: "",
      diabetic: "",
      physical_activity: "",
      gen_health: "",
      diff_walking: "",
      asthma: "",
      kidney_disease: "",
      skin_cancer: "",
      physical_health: null,
      mental_health: null,
      sleep_time: null,
    };
    this.log("Starting assessment flow.");
    return this.getUIState();
  }

  public handleNavigation(
    direction: "next" | "back",
    inputValue: any,
  ): {
    status: "QUESTIONING" | "READY_TO_SUBMIT";
    uiState?: AgentUIState;
    error?: string;
  } {
    if (direction === "back") {
      if (this.currentIndex > 0) {
        this.currentIndex--;
        this.log(`Navigating back. Current index is now ${this.currentIndex}.`);
        return { status: "QUESTIONING", uiState: this.getUIState() };
      }
      return { status: "QUESTIONING", uiState: this.getUIState() };
    }

    // Direction is "next"
    const currentQuestion = this.questions[this.currentIndex];
    this.log(`Validating value for ${currentQuestion.key}`, inputValue);

    if (!currentQuestion.validation(inputValue)) {
      this.log(`Validation failed for ${currentQuestion.key}.`, inputValue);
      return {
        status: "QUESTIONING",
        uiState: this.getUIState(),
        error: `Invalid value for ${currentQuestion.label}`,
      };
    }

    // Save validated input to state
    const key = currentQuestion.key;
    if (
      currentQuestion.type === "number" ||
      currentQuestion.type === "bmi_calculator"
    ) {
      this.formData[key] =
        inputValue === "" || inputValue === null
          ? null
          : Number.parseFloat(inputValue);
    } else {
      this.formData[key] = inputValue;
    }

    this.log(`Updated state for ${key}`, this.formData[key]);

    if (this.currentIndex < this.questions.length - 1) {
      this.currentIndex++;
      this.log(
        `Navigating forward. Current index is now ${this.currentIndex}.`,
      );
      return { status: "QUESTIONING", uiState: this.getUIState() };
    }

    // Finished last question
    this.log("All questions answered. Transitioning to ready to submit.");
    return { status: "READY_TO_SUBMIT" };
  }

  public isPayloadValid(): boolean {
    const data = this.formData;
    for (const q of this.questions) {
      const val = data[q.key];
      if (val === null || val === "") {
        this.log(
          `Final payload check failed: key '${q.key}' is missing or null.`,
        );
        return false;
      }
      if (!q.validation(val)) {
        this.log(
          `Final payload check failed: key '${q.key}' has invalid value:`,
          val,
        );
        return false;
      }
    }
    return true;
  }
}
export default DataCollectionAgent;
