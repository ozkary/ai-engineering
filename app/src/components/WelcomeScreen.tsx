import { Accessibility, Heart, ShieldCheck } from "lucide-react";
import type React from "react";

interface WelcomeScreenProps {
  onStart: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart }) => {
  return (
    <div className="flex flex-col items-center text-center p-6 md:p-10 max-w-lg mx-auto bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 transition-all duration-300">
      <div className="w-16 h-16 bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 rounded-full flex items-center justify-center mb-6 shadow-inner animate-pulse">
        <Heart className="w-8 h-8 fill-rose-500" />
      </div>

      <h1 className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight mb-3">
        Heart Disease Risk Assessment
      </h1>

      <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8">
        Welcome to the diagnostic intake portal. This interface collects
        clinical metrics and lifestyle attributes to compile a comprehensive
        profile for downstream heart disease risk classification.
      </p>

      <div className="w-full space-y-4 mb-8 text-left">
        {/* Security Info Card */}
        <div className="flex items-start gap-3 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-800 dark:text-emerald-300 p-4 rounded-xl border border-emerald-100 dark:border-emerald-900/30">
          <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">
              Security & Privacy Assurance
            </h4>
            <p className="text-xs text-emerald-700 dark:text-emerald-400 mt-0.5">
              For your privacy and security, no Personally Identifiable
              Information (PII) is collected or stored. All clinical metadata
              remains fully anonymized.
            </p>
          </div>
        </div>

        {/* Accessibility Info Card */}
        <div className="flex items-start gap-3 bg-indigo-50 dark:bg-indigo-950/20 text-indigo-800 dark:text-indigo-300 p-4 rounded-xl border border-indigo-100 dark:border-indigo-900/30">
          <Accessibility className="w-6 h-6 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Multi-Modal Accessibility</h4>
            <p className="text-xs text-indigo-700 dark:text-indigo-400 mt-0.5 leading-relaxed">
              This portal supports mouse interaction, keyboard hotkeys (Space to
              continue, M/F, Y/N, Backspace/Left Arrow to go back), and
              persistent hands-free voice control (speak answers or commands
              like "Next" or "Back").
            </p>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={onStart}
        className="w-full md:w-auto px-8 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        Start Assessment
      </button>
    </div>
  );
};
