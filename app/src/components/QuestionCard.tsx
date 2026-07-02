import type React from "react";
import { useEffect, useState } from "react";
import type { QuestionDefinition } from "../types";
import { SpeechToText } from "./SpeechToText";

interface QuestionCardProps {
  question: QuestionDefinition;
  value: any;
  onChange: (val: any) => void;
  gender?: string;
  isListening: boolean;
  onToggleListen: () => void;
  onSessionEnd: () => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  value,
  onChange,
  gender,
  isListening,
  onToggleListen,
  onSessionEnd,
}) => {
  const [useCalculator, setUseCalculator] = useState(false);
  const [bmiInputType, setBmiInputType] = useState<"imperial" | "metric">(
    "imperial",
  );
  const [weight, setWeight] = useState("");
  const [heightFeet, setHeightFeet] = useState("");
  const [heightInches, setHeightInches] = useState("");
  const [heightCm, setHeightCm] = useState("");

  // Filter options: if gender is Male, omit "Yes (during pregnancy)" from diabetes options
  const options = question.options
    ? question.key === "diabetic" && gender === "Male"
      ? question.options.filter((opt) => opt !== "Yes (during pregnancy)")
      : question.options
    : undefined;

  // Reset calculator states when switching questions to prevent state carryover
  // and fix the bug where typing/clicking gets wiped out by active calculator updates.
  // biome-ignore lint/correctness/useExhaustiveDependencies: Reset when question key changes
  useEffect(() => {
    setUseCalculator(false);
    setWeight("");
    setHeightFeet("");
    setHeightInches("");
    setHeightCm("");
  }, [question.key]);

  // Compute BMI dynamically whenever sub-fields change
  useEffect(() => {
    if (!useCalculator) return;

    let computedBmi: number | null = null;

    if (bmiInputType === "imperial") {
      const wLbs = Number.parseFloat(weight);
      const hFt = Number.parseFloat(heightFeet);
      const hIn = Number.parseFloat(heightInches || "0");

      if (
        !Number.isNaN(wLbs) &&
        !Number.isNaN(hFt) &&
        (hFt > 0 || hIn > 0) &&
        wLbs > 0
      ) {
        const totalHeightInches = hFt * 12 + hIn;
        computedBmi = (wLbs / (totalHeightInches * totalHeightInches)) * 703;
      }
    } else {
      const wKg = Number.parseFloat(weight);
      const hCm = Number.parseFloat(heightCm);

      if (!Number.isNaN(wKg) && !Number.isNaN(hCm) && hCm > 0 && wKg > 0) {
        const hM = hCm / 100;
        computedBmi = wKg / (hM * hM);
      }
    }

    if (computedBmi !== null && computedBmi >= 10 && computedBmi <= 60) {
      onChange(Number.parseFloat(computedBmi.toFixed(1)));
    } else {
      onChange("");
    }
  }, [
    useCalculator,
    bmiInputType,
    weight,
    heightFeet,
    heightInches,
    heightCm,
    onChange,
  ]);

  // Handle Speech Transcription
  const handleTranscription = (text: string) => {
    // Parse the transcription depending on question type
    if (question.type === "number" || question.type === "bmi_calculator") {
      // Find the first number in the transcript
      const match = text.match(/\d+(\.\d+)?/);
      if (match) {
        onChange(match[0]);
      } else {
        onChange(text);
      }
    } else if (question.type === "select") {
      // Look for fuzzy matches in options
      const normalized = text.toLowerCase().trim();
      const optionMatch = options?.find(
        (opt) =>
          opt.toLowerCase().includes(normalized) ||
          normalized.includes(opt.toLowerCase()),
      );
      if (optionMatch) {
        onChange(optionMatch);
      } else {
        onChange(text);
      }
    } else {
      onChange(text);
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const isBmiCalc = question.type === "bmi_calculator";

  return (
    <div className="w-full bg-white rounded-2xl p-6 md:p-8 border border-slate-100 shadow-lg">
      <div className="flex justify-between items-start gap-4 mb-6">
        <h2 className="text-xl font-bold text-slate-800 leading-snug">
          {question.label}
        </h2>
        {/* Only enable voice input for non-select, or select with simple options */}
        {(!isBmiCalc || !useCalculator) && (
          <div className="shrink-0">
            <SpeechToText
              onTranscription={handleTranscription}
              isListening={isListening}
              onToggleListen={onToggleListen}
              onSessionEnd={onSessionEnd}
            />
          </div>
        )}
      </div>

      <div className="space-y-6">
        {/* Render BMI Calculator wrapper */}
        {isBmiCalc && (
          <div className="mb-4">
            <div className="flex gap-4 border-b border-slate-100 pb-3 mb-4">
              <button
                type="button"
                onClick={() => {
                  setUseCalculator(false);
                  onChange("");
                }}
                className={`pb-2 px-1 font-semibold text-sm border-b-2 transition-all ${
                  !useCalculator
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-400 hover:text-slate-600"
                }`}
              >
                I know my BMI
              </button>
              <button
                type="button"
                onClick={() => {
                  setUseCalculator(true);
                  onChange("");
                  setWeight("");
                  setHeightFeet("");
                  setHeightInches("");
                  setHeightCm("");
                }}
                className={`pb-2 px-1 font-semibold text-sm border-b-2 transition-all ${
                  useCalculator
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-400 hover:text-slate-600"
                }`}
              >
                Calculate from Height/Weight
              </button>
            </div>

            {useCalculator && (
              <div className="bg-slate-50 p-4 rounded-xl space-y-4 border border-slate-100 animate-fadeIn">
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setBmiInputType("imperial");
                      setWeight("");
                      setHeightFeet("");
                      setHeightInches("");
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      bmiInputType === "imperial"
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                    }`}
                  >
                    Imperial (lbs / ft-in)
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setBmiInputType("metric");
                      setWeight("");
                      setHeightCm("");
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      bmiInputType === "metric"
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                    }`}
                  >
                    Metric (kg / cm)
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {bmiInputType === "imperial" ? (
                    <>
                      <div className="space-y-1.5">
                        <div className="block text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Height
                        </div>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            placeholder="Ft"
                            value={heightFeet}
                            onChange={(e) => setHeightFeet(e.target.value)}
                            className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 font-semibold focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                          />
                          <input
                            type="number"
                            placeholder="In"
                            value={heightInches}
                            onChange={(e) => setHeightInches(e.target.value)}
                            className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 font-semibold focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                          />
                        </div>
                      </div>
                      <div className="space-y-1.5">
                        <div className="block text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Weight (lbs)
                        </div>
                        <input
                          type="number"
                          placeholder="lbs"
                          value={weight}
                          onChange={(e) => setWeight(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 font-semibold focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="space-y-1.5">
                        <div className="block text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Height (cm)
                        </div>
                        <input
                          type="number"
                          placeholder="cm"
                          value={heightCm}
                          onChange={(e) => setHeightCm(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 font-semibold focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                        />
                      </div>
                      <div className="space-y-1.5">
                        <div className="block text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Weight (kg)
                        </div>
                        <input
                          type="number"
                          placeholder="kg"
                          value={weight}
                          onChange={(e) => setWeight(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 font-semibold focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                        />
                      </div>
                    </>
                  )}
                </div>

                {value && (
                  <div className="mt-2 p-2 bg-emerald-50 text-emerald-800 rounded-lg text-sm font-semibold text-center border border-emerald-100">
                    Computed BMI: {value}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Regular BMI Input or Numeric Inputs */}
        {((isBmiCalc && !useCalculator) || question.type === "number") && (
          <div className="space-y-2">
            <input
              type="number"
              value={value === null ? "" : value}
              onChange={handleTextChange}
              placeholder={isBmiCalc ? "e.g., 22.5" : "Enter a number"}
              className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100/50 border border-slate-200 rounded-xl text-slate-800 text-lg font-semibold focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition"
            />
            {isBmiCalc && (
              <p className="text-xs text-slate-400">
                Please enter a float between 10.0 and 60.0.
              </p>
            )}
            {!isBmiCalc && (
              <p className="text-xs text-slate-400">
                Please enter a value in the correct range (e.g. 0-30 for health
                days, 1-24 for sleep hours).
              </p>
            )}
          </div>
        )}

        {/* Select type options */}
        {question.type === "select" && options && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {options.map((opt) => {
              const isSelected = value === opt;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => onChange(opt)}
                  className={`p-4 text-left font-semibold rounded-xl border text-sm transition-all duration-200 focus:outline-none ${
                    isSelected
                      ? "bg-indigo-50 border-indigo-500 text-indigo-700 ring-2 ring-indigo-500"
                      : "bg-white hover:bg-slate-50 border-slate-200 text-slate-700 hover:text-slate-900"
                  }`}
                >
                  {opt}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
