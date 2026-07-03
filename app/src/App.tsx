import {
  AlertCircle,
  CheckCircle2,
  Home,
  Moon,
  RefreshCw,
  ShieldCheck,
  Sun,
} from "lucide-react";
import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DataCollectionAgent } from "./agent/DataCollectionAgent";
import { AccessibilityHelp } from "./components/AccessibilityHelp";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { NavigationControls } from "./components/NavigationControls";
import { QuestionCard } from "./components/QuestionCard";
import { SpeechToText } from "./components/SpeechToText";
import { TimelineRail } from "./components/TimelineRail";
import { WelcomeScreen } from "./components/WelcomeScreen";
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
        <div className="max-w-6xl mx-auto flex items-center justify-between">
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
                {/* Home Button */}
                <div className="flex justify-center items-center">
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
                    <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-450 shrink-0" />
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
                  onCancel={() => setStep("WELCOME")}
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
            <div className="relative w-full min-h-[70vh] flex items-center justify-center animate-fadeIn">
              {/* Left Drawer Panel: Timeline Progress Rail (fixed on desktop) */}
              <div className="hidden lg:block fixed left-0 top-16 bottom-[57px] z-30 w-80">
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
              <div className="max-w-2xl w-full space-y-4 z-10">
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 md:p-8 border border-slate-100 dark:border-slate-800 shadow-lg dark:shadow-slate-950/20 text-center space-y-6 w-full animate-fadeIn">
                  <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto shadow-inner">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    Assessment Ready
                  </h2>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed max-w-md mx-auto">
                    We have securely compiled your profile and are ready to submit
                    it for laboratory risk analysis.
                  </p>

                  {/* Validation Error Banner */}
                  {errorMsg && (
                    <div className="flex items-center gap-3 bg-rose-50 dark:bg-rose-950/20 text-rose-800 dark:text-rose-300 p-4 rounded-xl border border-rose-100 dark:border-rose-900/30 text-sm font-semibold text-left animate-shake">
                      <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-450 shrink-0" />
                      <span>{errorMsg}</span>
                    </div>
                  )}

                  {/* Inline list of answers to review/edit */}
                  <div className="text-left border border-slate-100 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-950/50 p-4 max-h-48 overflow-y-auto space-y-2">
                    <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">Review Your Answers</h3>
                    {agent.getQuestions().map((q) => (
                      <div key={q.key} className="flex justify-between items-center py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
                        <span className="text-xs font-medium text-slate-600 dark:text-slate-350">{q.label.split("?")[0]}</span>
                        <button
                          type="button"
                          onClick={() => {
                            handleJumpToQuestion(q.key);
                            setStep("QUESTIONING");
                          }}
                          className="text-xs font-bold text-indigo-600 dark:text-indigo-455 hover:text-indigo-800 dark:hover:text-indigo-300 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 px-2 py-1 rounded shadow-sm transition"
                        >
                          {formData[q.key] !== null && formData[q.key] !== "" ? String(formData[q.key]) : "Not Answered"}
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Medical Disclaimer Acknowledgment Checkbox */}
                  <div className="flex flex-col gap-4 border border-slate-100 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-950/50 p-4 text-left">
                    <label className="flex items-start gap-3 cursor-pointer text-slate-700 dark:text-slate-300 select-none">
                      <input
                        type="checkbox"
                        checked={acknowledged}
                        onChange={(e) => setAcknowledged(e.target.checked)}
                        className="mt-1 w-4 h-4 text-indigo-600 dark:text-indigo-400 border-slate-300 dark:border-slate-700 rounded focus:ring-indigo-500 cursor-pointer"
                      />
                      <span className="text-sm font-medium leading-relaxed">
                        I understand this is a suggestion tool, not a doctor's analysis, and it should not replace real medical review.
                      </span>
                    </label>
                    
                    <div className="flex items-center justify-between border-t border-slate-200/60 dark:border-slate-800 pt-3 mt-1 gap-4">
                      <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                        <p className="font-semibold text-slate-600 dark:text-slate-300">Voice Assistant:</p>
                        <p>• Check or Say <span className="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-indigo-600 dark:text-indigo-400">"yes"</span> for the check box.</p>
                        <p>• Also say <span className="font-mono bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-indigo-600 dark:text-indigo-400">"Send or click submit"</span> to submit the profile.</p>
                      </div>
                      <div className="shrink-0">
                        <SpeechToText
                          onTranscription={handleReadySpeech}
                          isListening={isListening}
                          onToggleListen={() => setVoiceEnabled(!voiceEnabled)}
                          onSessionEnd={() => setIsListening(false)}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center gap-4 pt-4">
                    <button
                      type="button"
                      onClick={handleStart}
                      className="px-6 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 font-semibold text-slate-600 dark:text-slate-400 transition"
                    >
                      Restart
                    </button>
                    <button
                      type="button"
                      onClick={() => setStep("WELCOME")}
                      className="px-6 py-2.5 rounded-lg border border-rose-200 dark:border-rose-900/30 hover:bg-rose-50 dark:hover:bg-rose-950/20 font-semibold text-rose-600 dark:text-rose-450 transition"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={handleSubmit}
                      disabled={!acknowledged}
                      className={`px-6 py-2.5 rounded-lg font-semibold shadow-sm transition ${
                        acknowledged
                          ? "bg-indigo-600 hover:bg-indigo-700 text-white hover:shadow cursor-pointer"
                          : "bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed"
                      }`}
                    >
                      Submit Profile
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Drawer Panel: Accessibility Help (fixed on desktop) */}
              <div className="hidden lg:block fixed right-0 top-16 bottom-[57px] z-30 w-80">
                <AccessibilityHelp />
              </div>
            </div>)}
            {step === "PROCESSING" && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-8 border border-slate-100 dark:border-slate-800 shadow-lg dark:shadow-slate-950/20 text-center max-w-2xl mx-auto w-full space-y-6 animate-fadeIn">
              <LoadingSpinner />
              {currentTip && (
                <div className="bg-indigo-50/80 dark:bg-indigo-950/20 border border-indigo-100/50 dark:border-indigo-900/30 rounded-xl p-4 animate-fadeIn max-w-md mx-auto">
                  <span className="text-xs font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-wider block mb-1">Health Tip</span>
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 leading-snug">{currentTip}</p>
                </div>
              )}
            </div>
          )}

          {step === "RESULTS" && (
            <div className="space-y-6 max-w-2xl mx-auto w-full">
              {/* Premium Results Presentation */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 md:p-8 border border-slate-100 dark:border-slate-800 shadow-xl dark:shadow-slate-950/20 space-y-6 text-center">
                <div className="w-16 h-16 rounded-full bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto shadow-inner">
                  <ShieldCheck className="w-8 h-8" />
                </div>

                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    Evaluation Complete
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                    The secure risk analysis pipeline has assessed your profile
                    against the reference machine learning model.
                  </p>
                </div>

                {riskResult && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-md mx-auto pt-2">
                    <div className="bg-slate-50 dark:bg-slate-950/30 rounded-xl p-4 border border-slate-100 dark:border-slate-850 flex flex-col justify-center items-center">
                      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Risk Category
                      </span>
                      <span
                        className={`text-xl font-extrabold uppercase mt-1 ${
                          riskResult.risk_category === "high"
                            ? "text-rose-600 dark:text-rose-400"
                            : riskResult.risk_category === "medium"
                              ? "text-amber-500 dark:text-amber-400"
                              : "text-emerald-600 dark:text-emerald-400"
                        }`}
                      >
                        {riskResult.risk_category}
                      </span>
                    </div>

                    <div className="bg-slate-50 dark:bg-slate-950/30 rounded-xl p-4 border border-slate-100 dark:border-slate-850 flex flex-col justify-center items-center">
                      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Probability Score
                      </span>
                      <span className="text-2xl font-extrabold text-slate-800 dark:text-slate-100 mt-1">
                        {(riskResult.raw_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )}

                {riskResult?.analysis && (
                  <div className="text-left bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100/55 dark:border-indigo-900/30 rounded-xl p-5 space-y-2 mt-4">
                    <h4 className="text-sm font-bold text-indigo-950 dark:text-indigo-300 uppercase tracking-wide">
                      Clinical Analyst & Health Coach Review
                    </h4>
                    <p className="text-sm text-slate-700 dark:text-slate-350 leading-relaxed whitespace-pre-wrap">
                      {riskResult.analysis}
                    </p>
                  </div>
                )}

                {riskResult?.disclosure && (
                  <div className="text-xs text-slate-400 dark:text-slate-500 text-left bg-amber-50/40 dark:bg-amber-955/10 border border-amber-100/50 dark:border-amber-900/30 rounded-lg p-3 italic">
                    {riskResult.disclosure}
                  </div>
                )}

                <details className="text-left bg-slate-900 rounded-xl p-4 font-mono text-xs text-slate-300 shadow-inner border border-slate-800">
                  <summary className="cursor-pointer font-sans font-semibold text-slate-400 dark:text-slate-500 hover:text-slate-200 dark:hover:text-slate-350 select-none pb-2">
                    View Technical Payload Data
                  </summary>
                  <pre className="overflow-x-auto max-h-48 pt-2 border-t border-slate-800">
                    {JSON.stringify(
                      {
                        features: formData,
                        prediction: {
                          raw_probability: riskResult?.raw_probability,
                          risk_category: riskResult?.risk_category,
                          analysis: riskResult?.analysis,
                        },
                      },
                      null,
                      2,
                    )}
                  </pre>
                </details>
              </div>

              <div className="flex justify-center gap-4">
                <button
                  type="button"
                  onClick={handleReset}
                  className="flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold rounded-lg border border-slate-200 dark:border-slate-800 transition shadow-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  Perform New Assessment
                </button>
                <button
                  type="button"
                  onClick={() => setStep("WELCOME")}
                  className="flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold rounded-lg border border-slate-200 dark:border-slate-800 transition shadow-sm"
                >
                  <Home className="w-4 h-4" />
                  Back to Landing Page
                </button>
                {riskResult?.analysis === "Unable to produce risk review narrative." && (
                  <button
                    type="button"
                    onClick={handleSubmit}
                    className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg border border-indigo-700 transition shadow-sm"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Retry Analysis
                  </button>
                )}
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
