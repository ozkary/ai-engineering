import { HelpCircle, Keyboard, Mic } from "lucide-react";
import type React from "react";

export const AccessibilityHelp: React.FC = () => {
  return (
    <aside className="w-full h-full bg-white p-6 border-l border-slate-200 overflow-y-auto space-y-6">
      {/* Header */}
      <div className="border-b border-slate-100 pb-3 flex items-center gap-2">
        <HelpCircle className="w-5 h-5 text-indigo-600" />
        <h3 className="text-base font-bold text-slate-900">
          Accessibility Options
        </h3>
      </div>

      {/* Content */}
      <div className="space-y-6">
        <p className="text-xs text-slate-500 leading-relaxed">
          Hands-free voice recognition and rapid-navigation shortcuts are active
          and available globally across the application.
        </p>

        {/* Section A: Voice Navigation */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Mic className="w-4 h-4 text-indigo-600" />
            <span>Voice Navigation</span>
          </div>

          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 space-y-3">
            <div className="flex justify-between items-start gap-2">
              <span className="text-xs text-slate-600 font-semibold">
                "Next" / "Continue"
              </span>
              <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-bold uppercase">
                Advance
              </span>
            </div>
            <p className="text-[11px] text-slate-500 pl-1 leading-normal">
              Advances the prompt to the next question when the current value is
              valid.
            </p>

            <div className="flex justify-between items-start gap-2 pt-2 border-t border-slate-200/50">
              <span className="text-xs text-slate-600 font-semibold">
                "Back"
              </span>
              <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-bold uppercase">
                Previous
              </span>
            </div>
            <p className="text-[11px] text-slate-500 pl-1 leading-normal">
              Navigates backward to the previous step in the flow.
            </p>

            <div className="flex justify-between items-start gap-2 pt-2 border-t border-slate-200/50">
              <span className="text-xs text-slate-600 font-semibold">
                Speak Answers
              </span>
              <span className="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-bold uppercase">
                Direct Input
              </span>
            </div>
            <p className="text-[11px] text-slate-500 pl-1 leading-normal">
              When the voice assistant mic is active, speak your selection or
              numeric answers clearly to submit them directly.
            </p>
          </div>
        </div>

        {/* Section B: Keyboard Hotkeys */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Keyboard className="w-4 h-4 text-indigo-600" />
            <span>Keyboard Hotkeys</span>
          </div>

          <div className="space-y-3 pl-1">
            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 font-medium">
                Continue
              </span>
              <kbd className="bg-slate-100 px-2 py-1 rounded text-xs font-mono border border-slate-200 shadow-sm shrink-0">
                Space
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 font-medium">
                Select "Yes"
              </span>
              <kbd className="bg-slate-100 px-2 py-1 rounded text-xs font-mono border border-slate-200 shadow-sm shrink-0">
                Y
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 font-medium">
                Select "No"
              </span>
              <kbd className="bg-slate-100 px-2 py-1 rounded text-xs font-mono border border-slate-200 shadow-sm shrink-0">
                N
              </kbd>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-xs text-slate-600 font-medium">
                Navigate Back
              </span>
              <div className="flex items-center gap-1.5 shrink-0">
                <kbd className="bg-slate-100 px-2 py-1 rounded text-xs font-mono border border-slate-200 shadow-sm">
                  Left Arrow
                </kbd>
                <span className="text-[10px] text-slate-400 font-semibold">
                  or
                </span>
                <kbd className="bg-slate-100 px-2 py-1 rounded text-xs font-mono border border-slate-200 shadow-sm">
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
