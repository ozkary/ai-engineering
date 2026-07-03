import {
  AlertCircle,  
  Home,
  Moon,  
  ShieldCheck,
  Sun,
} from "lucide-react";
import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DataCollectionAgent } from "./agent/DataCollectionAgent";
import { AccessibilityHelp } from "./components/AccessibilityHelp";
import { NavigationControls } from "./components/NavigationControls";
import { QuestionCard } from "./components/QuestionCard";
import { TimelineRail } from "./components/TimelineRail";
import { WelcomeScreen } from "./components/WelcomeScreen";
import { ReadyToSubmitScreen } from "./components/ReadyToSubmitScreen";
import { ProcessingScreen } from "./components/ProcessingScreen";
import { ResultsScreen } from "./components/ResultsScreen";
import type { AgentUIState, AppStepState, HeartDiseaseFormData } from "./types";
import healthTips from "./agent/health-tips.json";

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
    analysis?: string;
    disclosure?: string;
  } | null>(null);
  const [currentTip, setCurrentTip] = useState("");
  const [acknowledged, setAcknowledged] = useState(false);

  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) return saved === "true";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("darkMode", "true");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("darkMode", "false");
    }
  }, [darkMode]);

  // Rotate health tips every 5 seconds during processing
  useEffect(() => {
    if (step !== "PROCESSING") {
      setCurrentTip("");
      return;
    }

    const getRandomTip = () => {
      const idx = Math.floor(Math.random() * healthTips.length);
      return healthTips[idx];
    };
    setCurrentTip(getRandomTip());

    const interval = setInterval(() => {
      setCurrentTip(getRandomTip());
    }, 5000);

    return () => clearInterval(interval);
  }, [step]);

  // Synchronize and auto-restart isListening state when voiceEnabled is active
  // biome-ignore lint/correctness/useExhaustiveDependencies: Restart listening when index changes or step changes
  useEffect(() => {
    if (voiceEnabled && (step === "QUESTIONING" || step === "READY_TO_SUBMIT")) {
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
    setAcknowledged(false);
    const firstState = agent.start();
    setUiState(firstState);
    setFormData(agent.getFormData());
    setStep("QUESTIONING");
    setCurrentValue("");
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
        analysis: data.analysis,
        disclosure: data.disclosure,
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

  const handleReadySpeech = (text: string) => {
    const normalized = text.toLowerCase().trim();
    if (
      normalized === "cancel" ||
      normalized === "home" ||
      normalized === "go home" ||
      normalized.includes("cancel") ||
      normalized.includes("go home")
    ) {
      setStep("WELCOME");
      return;
    }

    if (
      normalized === "yes" ||
      normalized.includes("yes") ||
      normalized === "check" ||
      normalized.includes("check")
    ) {
      setAcknowledged(true);
      setErrorMsg(null);
    } else if (
      normalized === "send" ||
      normalized === "submit" ||
      normalized.includes("submit") ||
      normalized.includes("send")
    ) {
      if (acknowledged) {
        handleSubmit();
      } else {
        setErrorMsg("Please check or say 'yes' to the acknowledgment checkbox first.");
      }
    }
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

        // Hotkey selection support (a, b, c...) for age_category and gen_health
        const alphabet = "abcdefghijklmnop";
        const charIdx = alphabet.indexOf(key);
        if (
          (currentQuestion.key === "age_category" || currentQuestion.key === "gen_health") &&
          charIdx !== -1 &&
          charIdx < currentQuestion.options.length
        ) {
          e.preventDefault();
          setErrorMsg(null);
          setCurrentValue(currentQuestion.options[charIdx]);
          return;
        }

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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-between font-sans antialiased text-slate-800 dark:text-slate-100 transition-colors duration-200">
      {/* Top Header */}
      <header className="bg-slate-900 text-white py-4 px-6 shadow-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white shadow-md">
              H
            </div>
            <span className="font-bold text-lg tracking-tight">
              Heart Risk Assessment Portal
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label="Toggle dark mode"
              type="button"
            >
              {darkMode ? (
                <Sun className="w-4 h-4 text-amber-400 fill-amber-300" />
              ) : (
                <Moon className="w-4 h-4 text-slate-300" />
              )}
            </button>
            <span className="text-md font-semibold bg-slate-800 text-indigo-300 px-3 py-1.5 rounded-full border-slate-750 shadow-sm">
              Using AI Agents for Health
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow w-full px-4 md:px-8 py-6">
        <div className="w-full">
          {step === "WELCOME" && (
            <div className="max-w-2xl mx-auto w-full">
              <WelcomeScreen onStart={handleStart} />
            </div>
          )}

          {step === "QUESTIONING" && uiState && (
            <div className="w-full min-h-[70vh] grid grid-cols-1 lg:grid-cols-[20rem_1fr_20rem] gap-6 items-start">
              {/* Left Panel: Timeline Progress Rail */}
              <div className="hidden lg:block w-full">
                <TimelineRail
                  questions={agent.getQuestions()}
                  currentKey={uiState.targetFeatureKey}
                  formData={formData}
                  onJump={handleJumpToQuestion}
                />
              </div>

              {/* Center Panel: Questionnaire Card */}
              <div className="w-full max-w-3xl mx-auto space-y-4">
                {/* Home Button */}
                <div className="flex justify-between items-center">
                  <div className="flex-grow" />
                  <button
                    onClick={() => setStep("WELCOME")}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition shadow-sm cursor-pointer"
                    type="button"
                  >
                    <Home className="w-3.5 h-3.5" />
                    Back to Home
                  </button>
                </div>
                {/* Progress Indicator */}
                <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-100 dark:border-slate-800 shadow-sm">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-505 dark:text-slate-400 uppercase tracking-wider mb-2">
                    <span>
                      Question {currentQuestionNumber} of {totalQuestions}
                    </span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                      {progressPercent}% Completed
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-950 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-300 ease-out"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>
                </div>

                {/* Validation Error Banner */}
                {errorMsg && (
                  <div className="flex items-center gap-3 bg-rose-50 dark:bg-rose-950/20 text-rose-800 dark:text-rose-300 p-4 rounded-xl border border-rose-100 dark:border-rose-900/30 text-sm font-semibold animate-shake">
                    <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-455 shrink-0" />
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
                        normalized === "cancel" ||
                        normalized === "home" ||
                        normalized === "go home"
                      ) {
                        setStep("WELCOME");
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
                  onCancel={() => setStep("WELCOME")}
                  canBack={!uiState.isFirstQuestion}
                  canContinue={currentValue !== "" && currentValue !== null}
                  isLastQuestion={uiState.isLastQuestion}
                />
              </div>

              {/* Right Panel: Accessibility Help */}
              <div className="hidden lg:block w-full">
                <AccessibilityHelp />
              </div>
            </div>
          )}

          {step === "READY_TO_SUBMIT" && (
            <div className="w-full min-h-[70vh] grid grid-cols-1 lg:grid-cols-[20rem_1fr_20rem] gap-6 items-start animate-fadeIn">
              {/* Left Panel: Timeline Progress Rail */}
              <div className="hidden lg:block w-full">
                <TimelineRail
                  questions={agent.getQuestions()}
                  currentKey={"" as any}
                  formData={formData}
                  onJump={(key) => {
                    handleJumpToQuestion(key);
                    setStep("QUESTIONING");
                  }}
                />
              </div>

              {/* Center Panel: Submission Card */}
              <div className="w-full max-w-3xl mx-auto space-y-4">
                <ReadyToSubmitScreen
                  questions={agent.getQuestions()}
                  formData={formData}
                  acknowledged={acknowledged}
                  setAcknowledged={setAcknowledged}
                  errorMsg={errorMsg}
                  voiceEnabled={voiceEnabled}
                  setVoiceEnabled={setVoiceEnabled}
                  isListening={isListening}
                  setIsListening={setIsListening}
                  onRestart={handleStart}
                  onCancel={() => setStep("WELCOME")}
                  onSubmit={handleSubmit}
                  onJumpToQuestion={(key) => {
                    handleJumpToQuestion(key);
                    setStep("QUESTIONING");
                  }}
                  onReadySpeech={handleReadySpeech}
                />
              </div>

              {/* Right Panel: Accessibility Help */}
              <div className="hidden lg:block w-full">
                <AccessibilityHelp />
              </div>
            </div>
          )}

          {step === "PROCESSING" && (
            <ProcessingScreen currentTip={currentTip} />
          )}

          {step === "RESULTS" && (
            <ResultsScreen
              riskResult={riskResult}
              formData={formData}
              onReset={handleReset}
              onRetry={handleSubmit}
              onGoHome={() => setStep("WELCOME")}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-4 px-6 text-center text-xs border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2">
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
