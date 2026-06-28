import type React from "react";
import type { HeartDiseaseFormData, QuestionDefinition } from "../types";
import { Check, Edit3, User, Heart, ShieldAlert } from "lucide-react";

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
    <aside className="w-full h-full bg-white p-6 border-r border-slate-200 overflow-y-auto space-y-6">
      <div className="border-b border-slate-100 pb-3">
        <h3 className="text-base font-bold text-slate-900">
          Assessment Progress
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Click answered items to edit
        </p>
      </div>

      <div className="space-y-6">
        {groups.map((group) => (
          <div key={group.title} className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
              {group.icon}
              <span>{group.title}</span>
            </div>

            <div className="relative pl-3 border-l-2 border-slate-100 space-y-4 ml-2">
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
                          ? "bg-indigo-600 border-indigo-600 ring-4 ring-indigo-50 scale-125"
                          : isAnswered
                            ? "bg-emerald-500 border-emerald-500"
                            : "bg-white border-slate-300"
                      }`}
                    />

                    {/* Content Item */}
                    <button
                      type="button"
                      disabled={!isAnswered && !isActive}
                      onClick={() => onJump(key)}
                      className={`w-full text-left rounded-lg p-2 -m-2 transition-all flex flex-col ${
                        isActive
                          ? "bg-indigo-50/50 text-indigo-900 border border-indigo-100/50"
                          : isAnswered
                            ? "hover:bg-slate-50 cursor-pointer"
                            : "cursor-not-allowed opacity-60"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={`text-xs font-semibold ${
                            isActive
                              ? "text-indigo-700"
                              : isAnswered
                                ? "text-slate-700 group-hover:text-indigo-600"
                                : "text-slate-400"
                          }`}
                        >
                          {question.label.split("?")[0]}
                        </span>
                        {isAnswered && !isActive && (
                          <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 uppercase tracking-wider shrink-0 bg-emerald-50 px-1.5 py-0.5 rounded">
                            <Check className="w-2.5 h-2.5" />
                            <span>Done</span>
                          </div>
                        )}
                        {isActive && (
                          <div className="flex items-center gap-1 text-[10px] font-bold text-indigo-600 uppercase tracking-wider shrink-0 bg-indigo-50 px-1.5 py-0.5 rounded">
                            <Edit3 className="w-2.5 h-2.5" />
                            <span>Active</span>
                          </div>
                        )}
                      </div>

                      {isAnswered && (
                        <span className="text-xs text-slate-500 font-medium mt-1 pl-0.5">
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
