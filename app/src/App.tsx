import {
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DataCollectionAgent } from "./agent/DataCollectionAgent";
import { AccessibilityHelp } from "./components/AccessibilityHelp";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { NavigationControls } from "./components/NavigationControls";
import { QuestionCard } from "./components/QuestionCard";
import { TimelineRail } from "./components/TimelineRail";
import { WelcomeScreen } from "./components/WelcomeScreen";
import type { AgentUIState, AppStepState, HeartDiseaseFormData } from "./types";

export const App: React.FC = () => {
  // Initialize our reactive Data Collection Agent
  const agent = useMemo(() => new DataCollectionAgent(), []);

  const [step, setStep] = useState<AppStepState>("WELCOME");
  const [uiState, setUiState] = useState<AgentUIState | null>(null);
  const [currentValue, setCurrentValue] = useState<any>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [formData, setFormData] = useState<HeartDiseaseFormData>(
    agent.getFormData(),
  );
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [riskResult, setRiskResult] = useState<{
    raw_probability: number;
    risk_category: string;
  } | null>(null);

  // Synchronize and auto-restart isListening state when voiceEnabled is active
  // biome-ignore lint/correctness/useExhaustiveDependencies: Restart listening when index changes
  useEffect(() => {
    if (voiceEnabled && step === "QUESTIONING") {
      if (!isListening) {
        const timer = setTimeout(() => {
          setIsListening(true);
        }, 150);
        return () => clearTimeout(timer);
      }
    } else {
      setIsListening(false);
    }
  }, [voiceEnabled, step, agent.getCurrentIndex(), isListening]);

  const handleStart = () => {
    setErrorMsg(null);
    setRiskResult(null);
    const firstState = agent.start();
    setUiState(firstState);
    setCurrentValue("");
    setStep("QUESTIONING");
  };

  const handleContinue = useCallback(() => {
    if (!uiState) return;
    setErrorMsg(null);

    const result = agent.handleNavigation("next", currentValue);

    if (result.error) {
      setErrorMsg(result.error);
      return;
    }

    // Update form data in react state
    setFormData(agent.getFormData());

    if (result.status === "READY_TO_SUBMIT") {
      setStep("READY_TO_SUBMIT");
    } else if (result.status === "QUESTIONING" && result.uiState) {
      setUiState(result.uiState);
      // Pre-populate with previous value if it exists in form data
      const nextKey = result.uiState.targetFeatureKey;
      const nextVal = agent.getFormData()[nextKey];
      setCurrentValue(nextVal === null ? "" : nextVal);
    }
  }, [uiState, currentValue, agent]);

  const handleBack = useCallback(() => {
    setErrorMsg(null);
    const result = agent.handleNavigation("back", null);

    if (result.uiState) {
      setUiState(result.uiState);
      const prevKey = result.uiState.targetFeatureKey;
      const prevVal = agent.getFormData()[prevKey];
      setCurrentValue(prevVal === null ? "" : prevVal);
    }
  }, [agent]);

  const handleJumpToQuestion = (key: keyof HeartDiseaseFormData) => {
    setErrorMsg(null);
    const nextState = agent.jumpToQuestion(key);
    setUiState(nextState);
    const nextVal = agent.getFormData()[key];
    setCurrentValue(nextVal === null ? "" : nextVal);
  };

  const handleSubmit = async () => {
    if (!agent.isPayloadValid()) {
      setErrorMsg("Payload validation failed. Please check all values.");
      return;
    }
    setStep("PROCESSING");
    setErrorMsg(null);

    // Print to browser console as required by specs
    console.log(
      "HeartDiseaseFormData JSON Payload captured successfully:",
      agent.getFormData(),
    );

    try {
      const response = await fetch("/api/evaluate-risk", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to retrieve risk assessment.");
      }

      setRiskResult({
        raw_probability: data.raw_probability,
        risk_category: data.risk_category,
      });
      setStep("RESULTS");
    } catch (err: any) {
      console.error("Submission error:", err);
      setErrorMsg(err.message || "Unable to contact secure evaluation server.");
      setStep("READY_TO_SUBMIT");
    }
  };

  const handleReset = () => {
    handleStart();
  };

  // Hotkey support: Y/y selects Yes, N/n selects No, Spacebar continues.
  useEffect(() => {
    if (step !== "QUESTIONING" || !uiState) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement;
      const isInput =
        activeEl &&
        (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA");

      // Handle Spacebar to continue
      if (e.key === " " || e.key === "Spacebar") {
        const canCont = currentValue !== "" && currentValue !== null;
        if (canCont) {
          e.preventDefault();
          handleContinue();
        }
        return;
      }

      // Ignore text input fields for Y/N/back shortcuts
      if (isInput) return;

      // Handle Backspace or Left Arrow to navigate back
      if (e.key === "Backspace" || e.key === "ArrowLeft") {
        if (!uiState.isFirstQuestion) {
          e.preventDefault();
          handleBack();
        }
        return;
      }

      const currentQuestion = agent.getQuestions()[agent.getCurrentIndex()];
      if (
        currentQuestion &&
        currentQuestion.type === "select" &&
        currentQuestion.options
      ) {
        const key = e.key.toLowerCase();
        if (key === "y") {
          const yesOpt = currentQuestion.options.find(
            (opt) =>
              opt.toLowerCase() === "yes" || opt.toLowerCase().startsWith("y"),
          );
          if (yesOpt) {
            e.preventDefault();
            setErrorMsg(null);
            setCurrentValue(yesOpt);
          }
        } else if (key === "n") {
          const noOpt = currentQuestion.options.find(
            (opt) =>
              opt.toLowerCase() === "no" || opt.toLowerCase().startsWith("n"),
          );
          if (noOpt) {
            e.preventDefault();
            setErrorMsg(null);
            setCurrentValue(noOpt);
          }
        } else if (key === "m") {
          const maleOpt = currentQuestion.options.find(
            (opt) => opt.toLowerCase() === "male",
          );
          if (maleOpt) {
            e.preventDefault();
            setErrorMsg(null);
            setCurrentValue(maleOpt);
          }
        } else if (key === "f") {
          const femaleOpt = currentQuestion.options.find(
            (opt) => opt.toLowerCase() === "female",
          );
          if (femaleOpt) {
            e.preventDefault();
            setErrorMsg(null);
            setCurrentValue(femaleOpt);
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [step, uiState, currentValue, handleContinue, agent, handleBack]);

  // Progress metrics calculation
  const totalQuestions = agent.getQuestions().length;
  const currentQuestionNumber = agent.getCurrentIndex() + 1;
  const progressPercent = Math.round(
    (currentQuestionNumber / totalQuestions) * 100,
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between font-sans antialiased text-slate-800">
      {/* Top Header */}
      <header className="bg-slate-900 text-white py-4 px-6 shadow-md border-b border-slate-800">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white shadow-md">
              H
            </div>
            <span className="font-bold text-lg tracking-tight">
              Heart Risk Assessment Portal
            </span>
          </div>
          <span className="text-xs font-semibold bg-slate-800 text-indigo-300 px-3 py-1.5 rounded-full border border-slate-700 shadow-sm">
            Phase 1 UI Layer
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow flex items-start justify-center p-4 md:p-8 max-w-6xl w-full mx-auto">
        <div className="w-full">
          {step === "WELCOME" && (
            <div className="max-w-2xl mx-auto w-full">
              <WelcomeScreen onStart={handleStart} />
            </div>
          )}

          {step === "QUESTIONING" && uiState && (
            <div className="relative w-full min-h-[70vh] flex items-center justify-center">
              {/* Left Drawer Panel: Timeline Progress Rail (fixed on desktop) */}
              <div className="hidden lg:block fixed left-0 top-16 bottom-[57px] z-30 w-80">
                <TimelineRail
                  questions={agent.getQuestions()}
                  currentKey={uiState.targetFeatureKey}
                  formData={formData}
                  onJump={handleJumpToQuestion}
                />
              </div>

              {/* Center Panel: Questionnaire Card */}
              <div className="max-w-2xl w-full space-y-4 z-10">
                {/* Progress Indicator */}
                <div className="bg-white rounded-xl p-4 border border-slate-100 shadow-sm">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    <span>
                      Question {currentQuestionNumber} of {totalQuestions}
                    </span>
                    <span className="text-indigo-600 font-bold">
                      {progressPercent}% Completed
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-300 ease-out"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>
                </div>

                {/* Validation Error Banner */}
                {errorMsg && (
                  <div className="flex items-center gap-3 bg-rose-50 text-rose-800 p-4 rounded-xl border border-rose-100 text-sm font-semibold animate-shake">
                    <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                {/* The Question Card */}
                <QuestionCard
                  question={agent.getQuestions()[agent.getCurrentIndex()]}
                  value={currentValue}
                  onChange={(val) => {
                    setErrorMsg(null);
                    if (typeof val === "string") {
                      const normalized = val.toLowerCase().trim();
                      if (
                        normalized === "next" ||
                        normalized === "continue" ||
                        normalized === "go next"
                      ) {
                        const canCont =
                          currentValue !== "" && currentValue !== null;
                        if (canCont) {
                          handleContinue();
                        }
                        return;
                      }
                      if (normalized === "back" || normalized === "go back") {
                        if (!uiState.isFirstQuestion) {
                          handleBack();
                        }
                        return;
                      }
                      if (
                        normalized === "restart" ||
                        normalized === "start again" ||
                        normalized === "reset"
                      ) {
                        handleStart();
                        return;
                      }
                    }

                    setCurrentValue(val);
                  }}
                  gender={formData.sex}
                  isListening={isListening}
                  onToggleListen={() => setVoiceEnabled(!voiceEnabled)}
                  onSessionEnd={() => setIsListening(false)}
                />

                {/* Navigation Bar */}
                <NavigationControls
                  onBack={handleBack}
                  onContinue={handleContinue}
                  onRestart={handleStart}
                  canBack={!uiState.isFirstQuestion}
                  canContinue={currentValue !== "" && currentValue !== null}
                  isLastQuestion={uiState.isLastQuestion}
                />
              </div>

              {/* Right Drawer Panel: Accessibility Help (fixed on desktop) */}
              <div className="hidden lg:block fixed right-0 top-16 bottom-[57px] z-30 w-80">
                <AccessibilityHelp />
              </div>
            </div>
          )}

          {step === "READY_TO_SUBMIT" && (
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-slate-100 shadow-lg text-center space-y-6 max-w-2xl mx-auto w-full">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800">
                Assessment Ready
              </h2>
              <p className="text-slate-600 leading-relaxed max-w-md mx-auto">
                We have securely compiled your profile and are ready to submit
                it for laboratory risk analysis.
              </p>

              <div className="flex justify-center gap-4 pt-4">
                <button
                  type="button"
                  onClick={handleStart}
                  className="px-6 py-2.5 rounded-lg border border-slate-200 hover:bg-slate-50 font-semibold text-slate-600 transition"
                >
                  Restart
                </button>
                <button
                  type="button"
                  onClick={handleSubmit}
                  className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm hover:shadow transition"
                >
                  Submit Profile
                </button>
              </div>
            </div>
          )}

          {step === "PROCESSING" && (
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-lg text-center max-w-2xl mx-auto w-full">
              <LoadingSpinner />
            </div>
          )}

          {step === "RESULTS" && (
            <div className="space-y-6 max-w-2xl mx-auto w-full">
              {/* Premium Results Presentation */}
              <div className="bg-white rounded-2xl p-6 md:p-8 border border-slate-100 shadow-xl space-y-6 text-center">
                <div className="w-16 h-16 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto shadow-inner">
                  <ShieldCheck className="w-8 h-8" />
                </div>

                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-slate-800">
                    Evaluation Complete
                  </h3>
                  <p className="text-sm text-slate-500 max-w-sm mx-auto">
                    The secure risk analysis pipeline has assessed your profile
                    against the reference machine learning model.
                  </p>
                </div>

                {riskResult && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-md mx-auto pt-2">
                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 flex flex-col justify-center items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Risk Category
                      </span>
                      <span
                        className={`text-xl font-extrabold uppercase mt-1 ${
                          riskResult.risk_category === "high"
                            ? "text-rose-600"
                            : riskResult.risk_category === "medium"
                              ? "text-amber-500"
                              : "text-emerald-600"
                        }`}
                      >
                        {riskResult.risk_category}
                      </span>
                    </div>

                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 flex flex-col justify-center items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Probability Score
                      </span>
                      <span className="text-2xl font-extrabold text-slate-800 mt-1">
                        {(riskResult.raw_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )}

                <details className="text-left bg-slate-900 rounded-xl p-4 font-mono text-xs text-slate-300 shadow-inner border border-slate-800">
                  <summary className="cursor-pointer font-sans font-semibold text-slate-400 hover:text-slate-200 select-none pb-2">
                    View Technical Payload Data
                  </summary>
                  <pre className="overflow-x-auto max-h-48 pt-2 border-t border-slate-800">
                    {JSON.stringify(
                      {
                        features: formData,
                        prediction: riskResult,
                      },
                      null,
                      2,
                    )}
                  </pre>
                </details>
              </div>

              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={handleReset}
                  className="flex items-center gap-2 px-6 py-2.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-lg border border-slate-200 transition shadow-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  Perform New Assessment
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-4 px-6 text-center text-xs border-t border-slate-800">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2">
          <span>&copy; 2026 Heart Risk Inc. All rights reserved.</span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            Anonymized Endpoint - Zero PII Storage
          </span>
        </div>
      </footer>
    </div>
  );
};
export default App;
