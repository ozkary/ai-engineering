import type React from "react";
import { ShieldCheck, RefreshCw, Home } from "lucide-react";
import type { HeartDiseaseFormData } from "../types";

interface ResultsScreenProps {
  riskResult: {
    raw_probability: number;
    risk_category: string;
    analysis?: string;
    disclosure?: string;
  } | null;
  formData: HeartDiseaseFormData;
  onReset: () => void;
  onRetry: () => void;
  onGoHome: () => void;
}

export const ResultsScreen: React.FC<ResultsScreenProps> = ({
  riskResult,
  formData,
  onReset,
  onRetry,
  onGoHome,
}) => {
  return (
    <div className="space-y-6 max-w-2xl mx-auto w-full">
      {/* Premium Results Presentation */}
      <div className="bg-slate-100 dark:bg-slate-900 rounded-2xl p-6 md:p-8 border border-slate-100 dark:border-slate-800 shadow-xl dark:shadow-slate-950/20 space-y-6 text-center">
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
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {riskResult.analysis}
            </p>
          </div>
        )}

        {riskResult?.disclosure && (
          <div className="text-sm text-slate-500 dark:text-slate-400 text-left bg-slate-50/50 dark:bg-slate-950/40 border border-slate-200/50 dark:border-slate-800/80 rounded-lg p-3">
            {riskResult.disclosure}
          </div>
        )}

        <details className="text-left bg-slate-900 rounded-xl p-4 font-mono text-xs text-slate-300 shadow-inner border border-slate-800">
          <summary className="cursor-pointer font-sans font-semibold text-slate-400 dark:text-slate-500 hover:text-slate-200 dark:hover:text-slate-300 select-none pb-2">
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
          onClick={onReset}
          className="flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold rounded-lg border border-slate-200 dark:border-slate-800 transition shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
          Perform New Assessment
        </button>
        <button
          type="button"
          onClick={onGoHome}
          className="flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold rounded-lg border border-slate-200 dark:border-slate-800 transition shadow-sm"
        >
          <Home className="w-4 h-4" />
          Back to Landing Page
        </button>
        {riskResult?.analysis === "Unable to produce risk review narrative." && (
          <button
            type="button"
            onClick={onRetry}
            className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg border border-indigo-700 transition shadow-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Analysis
          </button>
        )}
      </div>
    </div>
  );
};
export default ResultsScreen;
