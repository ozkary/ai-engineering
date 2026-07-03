import type React from "react";
import { LoadingSpinner } from "./LoadingSpinner";

interface ProcessingScreenProps {
  currentTip: string;
}

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({
  currentTip,
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-8 border border-slate-100 dark:border-slate-800 shadow-lg dark:shadow-slate-950/20 text-center max-w-2xl mx-auto w-full space-y-6 animate-fadeIn">
      <LoadingSpinner />
      {currentTip && (
        <div className="bg-indigo-50/80 dark:bg-indigo-950/20 border border-indigo-100/50 dark:border-indigo-900/30 rounded-xl p-4 animate-fadeIn max-w-md mx-auto">
          <span className="text-xs font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-wider block mb-1">Health Tip</span>
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-355 leading-snug">{currentTip}</p>
        </div>
      )}
    </div>
  );
};
export default ProcessingScreen;
