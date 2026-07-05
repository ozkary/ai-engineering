import { HelpCircle, Keyboard, Mic } from "lucide-react";
import type React from "react";

export const AccessibilityHelp: React.FC = () => {
  return (
    <aside className="w-full h-full max-h-[calc(100vh-12rem)] bg-slate-100 dark:bg-slate-900 p-6 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-y-auto space-y-6">
      {/* Header */}
      <div className="border-b border-slate-100 dark:border-slate-800 pb-3 flex items-center gap-2">
        <HelpCircle className="w-5 h-5 text-indigo-600" />
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Accessibility Options
        </h3>
      </div>

      {/* Content */}
      <div className="space-y-6">
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Hands-free voice recognition and rapid-navigation shortcuts are active
          and available globally across the application.
        </p>

        {/* Section A: Voice Navigation */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            <Mic className="w-4 h-4 text-indigo-600" />
            <span>Voice Navigation</span>
          </div>

          <div className="bg-slate-50 dark:bg-slate-950/20 rounded-xl p-4 border border-slate-100 dark:border-slate-900/30 space-y-3">
            <div className="flex justify-between items-start gap-2">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-semibold">
                "Next" / "Continue"
              </span>
              <span className="text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-1.5 py-0.5 rounded font-bold uppercase">
                Advance
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 pl-1 leading-normal">
              Advances the prompt to the next question when the current value is
              valid.
            </p>

            <div className="flex justify-between items-start gap-2 pt-2 border-t border-slate-200/50 dark:border-slate-800">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-semibold">
                "Back"
              </span>
              <span className="text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-1.5 py-0.5 rounded font-bold uppercase">
                Previous
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 pl-1 leading-normal">
              Navigates backward to the previous step in the flow.
            </p>

            <div className="flex justify-between items-start gap-2 pt-2 border-t border-slate-200/50 dark:border-slate-800">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-semibold">
                Speak Answers
              </span>
              <span className="text-[10px] bg-indigo-50 dark:bg-indigo-950/30 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.5 rounded font-bold uppercase">
                Direct Input
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 pl-1 leading-normal">
              When the voice assistant mic is active, speak your selection or
              numeric answers clearly to submit them directly.
            </p>
          </div>
        </div>

        {/* Section B: Keyboard Hotkeys */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            <Keyboard className="w-4 h-4 text-indigo-600" />
            <span>Keyboard Hotkeys</span>
          </div>

          <div className="space-y-3 pl-1">
            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                Continue
              </span>
              <kbd className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono border border-slate-200 dark:border-slate-700 shadow-sm shrink-0">
                Space
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                Select "Yes"
              </span>
              <kbd className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono border border-slate-200 dark:border-slate-700 shadow-sm shrink-0">
                Y
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                Select "No"
              </span>
              <kbd className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono border border-slate-200 dark:border-slate-700 shadow-sm shrink-0">
                N
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                Navigate Back
              </span>
              <div className="flex items-center gap-1.5 shrink-0">
                <kbd className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono border border-slate-200 dark:border-slate-700 shadow-sm">
                  Left Arrow
                </kbd>
                <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold">
                  or
                </span>
                <kbd className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono border border-slate-200 dark:border-slate-700 shadow-sm">
                  Backspace
                </kbd>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
