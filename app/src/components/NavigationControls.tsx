import { ArrowLeft, ArrowRight } from "lucide-react";
import type React from "react";

interface NavigationControlsProps {
  onBack: () => void;
  onContinue: () => void;
  onRestart: () => void;
  canBack: boolean;
  canContinue: boolean;
  isLastQuestion: boolean;
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  onBack,
  onContinue,
  onRestart,
  canBack,
  canContinue,
  isLastQuestion,
}) => {
  return (
    <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-100 w-full gap-4">
      <button
        type="button"
        onClick={onBack}
        disabled={!canBack}
        className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
          canBack
            ? "text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100"
            : "text-slate-300 bg-slate-50 cursor-not-allowed"
        }`}
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <button
        type="button"
        onClick={onRestart}
        className="px-5 py-2.5 rounded-lg font-medium text-sm text-slate-500 hover:text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 transition-all duration-200 shadow-sm"
      >
        Start Again
      </button>

      <button
        type="button"
        onClick={onContinue}
        disabled={!canContinue}
        className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 shadow-sm ${
          canContinue
            ? "text-white bg-indigo-600 hover:bg-indigo-700 hover:shadow"
            : "text-slate-400 bg-slate-100 cursor-not-allowed"
        }`}
      >
        {isLastQuestion ? "Continue to Analysis" : "Continue"}
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
};
