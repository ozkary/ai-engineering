import { ArrowLeft, ArrowRight } from "lucide-react";
import type React from "react";

interface NavigationControlsProps {
  onBack: () => void;
  onContinue: () => void;
  onRestart: () => void;
  onCancel?: () => void;
  canBack: boolean;
  canContinue: boolean;
  isLastQuestion: boolean;
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  onBack,
  onContinue,
  onRestart,
  onCancel,
  canBack,
  canContinue,
  isLastQuestion,
}) => {
  return (
    <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 w-full gap-4">
      <button
        type="button"
        onClick={onBack}
        disabled={!canBack}
        className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
          canBack
            ? "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800"
            : "text-slate-300 dark:text-slate-600 bg-slate-50 dark:bg-slate-900 cursor-not-allowed"
        }`}
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onRestart}
          className="px-4 py-2.5 rounded-lg font-medium text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 transition-all duration-200 shadow-sm"
        >
          Start Again
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2.5 rounded-lg font-medium text-sm text-rose-600 dark:text-rose-450 hover:bg-rose-50 dark:hover:bg-rose-950/20 bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/30 transition-all duration-200 shadow-sm"
          >
            Cancel
          </button>
        )}
      </div>

      <button
        type="button"
        onClick={onContinue}
        disabled={!canContinue}
        className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 shadow-sm ${
          canContinue
            ? "text-white bg-indigo-600 hover:bg-indigo-700 hover:shadow"
            : "text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 cursor-not-allowed"
        }`}
      >
        {isLastQuestion ? "Continue to Analysis" : "Continue"}
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
};
