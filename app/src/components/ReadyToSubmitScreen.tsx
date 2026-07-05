import type React from "react";
import { CheckCircle2, AlertCircle } from "lucide-react";
import type { HeartDiseaseFormData, QuestionDefinition } from "../types";
import { SpeechToText } from "./SpeechToText";

interface ReadyToSubmitScreenProps {
  questions: QuestionDefinition[];
  formData: HeartDiseaseFormData;
  acknowledged: boolean;
  setAcknowledged: (val: boolean) => void;
  errorMsg: string | null;
  voiceEnabled: boolean;
  setVoiceEnabled: (val: boolean) => void;
  isListening: boolean;
  setIsListening: (val: boolean) => void;
  onRestart: () => void;
  onCancel: () => void;
  onSubmit: () => void;
  onJumpToQuestion: (key: keyof HeartDiseaseFormData) => void;
  onReadySpeech: (text: string) => void;
}

export const ReadyToSubmitScreen: React.FC<ReadyToSubmitScreenProps> = ({
  questions,
  formData,
  acknowledged,
  setAcknowledged,
  errorMsg,
  voiceEnabled,
  setVoiceEnabled,
  isListening,
  setIsListening,
  onRestart,
  onCancel,
  onSubmit,
  onJumpToQuestion,
  onReadySpeech,
}) => {
  return (
    <div className="bg-slate-100 dark:bg-slate-900 rounded-2xl p-6 md:p-8 border border-slate-100 dark:border-slate-800 shadow-lg dark:shadow-slate-950/20 text-center space-y-6 w-full animate-fadeIn">
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
          <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-455 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Inline list of answers to review/edit */}
      <div className="text-left border border-slate-100 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-950/50 p-4 max-h-48 overflow-y-auto space-y-2">
        <h3 className="text-xs font-bold text-slate-400 dark:text-slate-505 uppercase tracking-wider mb-2">Review Your Answers</h3>
        {questions.map((q) => (
          <div key={q.key} className="flex justify-between items-center py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
            <span className="text-xs font-medium text-slate-600 dark:text-slate-355">{q.label.split("?")[0]}</span>
            <button
              type="button"
              onClick={() => onJumpToQuestion(q.key)}
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
              onTranscription={onReadySpeech}
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
          onClick={onRestart}
          className="px-6 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 font-semibold text-slate-600 dark:text-slate-400 transition"
        >
          Restart
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2.5 rounded-lg border border-rose-200 dark:border-rose-900/30 hover:bg-rose-50 dark:hover:bg-rose-955/20 font-semibold text-rose-600 dark:text-rose-450 transition"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={onSubmit}
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
  );
};
export default ReadyToSubmitScreen;
