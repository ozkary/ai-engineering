import { Check, Edit3, Heart, ShieldAlert, User } from "lucide-react";
import type React from "react";
import type { HeartDiseaseFormData, QuestionDefinition } from "../types";

interface TimelineRailProps {
  questions: QuestionDefinition[];
  currentKey: keyof HeartDiseaseFormData;
  formData: HeartDiseaseFormData;
  onJump: (key: keyof HeartDiseaseFormData) => void;
}

interface GroupDefinition {
  title: string;
  icon: React.ReactNode;
  keys: (keyof HeartDiseaseFormData)[];
}

export const TimelineRail: React.FC<TimelineRailProps> = ({
  questions,
  currentKey,
  formData,
  onJump,
}) => {
  // Define groups
  const groups: GroupDefinition[] = [
    {
      title: "Demographics",
      icon: <User className="w-4 h-4" />,
      keys: ["sex", "age_category", "bmi"],
    },
    {
      title: "Lifestyle Factors",
      icon: <Heart className="w-4 h-4 text-rose-500 fill-rose-100" />,
      keys: [
        "smoking",
        "alcohol_drinking",
        "physical_activity",
        "gen_health",
        "physical_health",
        "mental_health",
        "sleep_time",
      ],
    },
    {
      title: "Medical History",
      icon: <ShieldAlert className="w-4 h-4 text-indigo-500" />,
      keys: [
        "stroke",
        "diabetic",
        "diff_walking",
        "asthma",
        "kidney_disease",
        "skin_cancer",
      ],
    },
  ];

  // Helper to format values for display
  const formatDisplayValue = (val: any) => {
    if (val === null || val === "") return "";
    if (typeof val === "number") return val.toString();
    return val;
  };

  return (
    <aside className="w-full h-full max-h-[calc(100vh-12rem)] bg-slate-100 dark:bg-slate-900 p-6 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-y-auto space-y-6">
      <div className="border-b border-slate-100 dark:border-slate-800 pb-3">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Assessment Progress
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Click answered items to edit
        </p>
      </div>

      <div className="space-y-6">
        {groups.map((group) => (
          <div key={group.title} className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              {group.icon}
              <span>{group.title}</span>
            </div>

            <div className="relative pl-3 border-l-2 border-slate-100 dark:border-slate-800 space-y-4 ml-2">
              {group.keys.map((key) => {
                const question = questions.find((q) => q.key === key);
                if (!question) return null;

                const value = formData[key];
                const isAnswered = value !== null && value !== "";
                const isActive = currentKey === key;

                return (
                  <div
                    key={key}
                    className="relative group flex items-start gap-3 text-left"
                  >
                    {/* Timeline Node Point */}
                    <div
                      className={`absolute -left-[19px] top-1 w-3 h-3 rounded-full border-2 transition-all ${
                        isActive
                          ? "bg-indigo-600 border-indigo-600 ring-4 ring-indigo-50 dark:ring-indigo-950 scale-125"
                          : isAnswered
                            ? "bg-emerald-500 border-emerald-500"
                            : "bg-white dark:bg-slate-950 border-slate-300 dark:border-slate-700"
                      }`}
                    />

                    {/* Content Item */}
                    <button
                      type="button"
                      disabled={!isAnswered && !isActive}
                      onClick={() => onJump(key)}
                      className={`w-full text-left rounded-lg p-2 -m-2 transition-all flex flex-col ${
                        isActive
                          ? "bg-indigo-50/50 dark:bg-indigo-950/20 text-indigo-900 dark:text-indigo-200 border border-indigo-100/50 dark:border-indigo-900/30"
                          : isAnswered
                            ? "hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer"
                            : "cursor-not-allowed opacity-60 text-slate-400 dark:text-slate-500"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={`text-xs font-semibold ${
                            isActive
                              ? "text-indigo-700 dark:text-indigo-400"
                              : isAnswered
                                ? "text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400"
                                : "text-slate-400 dark:text-slate-500"
                          }`}
                        >
                          {question.label.split("?")[0]}
                        </span>
                        {isAnswered && !isActive && (
                          <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider shrink-0 bg-emerald-50 dark:bg-emerald-950/30 px-1.5 py-0.5 rounded">
                            <Check className="w-2.5 h-2.5" />
                            <span>Done</span>
                          </div>
                        )}
                        {isActive && (
                          <div className="flex items-center gap-1 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider shrink-0 bg-indigo-50 dark:bg-indigo-950/30 px-1.5 py-0.5 rounded">
                            <Edit3 className="w-2.5 h-2.5" />
                            <span>Active</span>
                          </div>
                        )}
                      </div>

                      {isAnswered && (
                        <span className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1 pl-0.5">
                          {formatDisplayValue(value)}
                        </span>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};
