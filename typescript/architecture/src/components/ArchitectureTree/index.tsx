import { FileCode, Folder } from "lucide-react";

/**
 * @file  src/components/ArchitectureTree/index.tsx
 * @description  visualizes the folder structure of the architecture
 *
 * @author ogarcia (ozkary)
 *
 */
const ArchitectureTree = () => {
  return (
    <div className="font-mono text-sm text-slate-400 leading-relaxed bg-slate-950 p-6 rounded-lg border border-slate-800">
      <div className="flex items-center gap-2 text-slate-200 mb-2"><Folder size={16} className="text-amber-400"/> src/</div>
      <div className="pl-6 border-l border-slate-800 ml-2">
        <div className="flex items-center gap-2 mb-2 group"><Folder size={16} className="text-cyan-600"/> <span className="text-cyan-200">apis/</span></div>
        <div className="pl-6 border-l border-slate-800 ml-2 mb-2">
           <div className="flex items-center gap-2 mt-1"><Folder size={14} className="text-cyan-600"/> <span className="text-cyan-200">salesDashboard/</span> <span className="text-xs text-amber-500/70 border border-amber-500/20 px-1 rounded">camelCase</span></div>
           <div className="pl-6 border-l border-slate-800 ml-2 mt-1"><div className="flex items-center gap-2 text-slate-300"><FileCode size={14} className="text-blue-400"/> index.ts</div></div>
        </div>

        <div className="flex items-center gap-2 mb-2 mt-4 group"><Folder size={16} className="text-purple-600"/> <span className="text-purple-200">services/</span></div>
        <div className="pl-6 border-l border-slate-800 ml-2 mb-2">
           <div className="flex items-center gap-2"><Folder size={14} className="text-purple-600"/> <span className="text-purple-200">salesDashboard/</span> <span className="text-xs text-amber-500/70 border border-amber-500/20 px-1 rounded">camelCase</span></div>
           <div className="pl-6 border-l border-slate-800 ml-2 mt-1"><div className="flex items-center gap-2 text-slate-300"><FileCode size={14} className="text-blue-400"/> index.ts</div></div>
        </div>

        {/* Components Folder - NEW */}
        <div className="flex items-center gap-2 mb-2 mt-4 group"><Folder size={16} className="text-indigo-600"/> <span className="text-indigo-200">components/</span></div>
        <div className="pl-6 border-l border-slate-800 ml-2 mb-2">
           <div className="flex items-center gap-2"><Folder size={14} className="text-indigo-600"/> <span className="text-indigo-200">SalesDashboard/</span> <span className="text-xs text-cyan-500/70 border border-cyan-500/20 px-1 rounded">PascalCase</span></div>
           <div className="pl-6 border-l border-slate-800 ml-2 mt-1">
              <div className="flex items-center gap-2 text-slate-300"><FileCode size={14} className="text-blue-400"/> controller.ts <span className="text-slate-500 italic">// Logic</span></div>
              <div className="flex items-center gap-2 text-amber-300 mt-1"><FileCode size={14} className="text-amber-500"/> index.tsx <span className="text-slate-500 italic">// View</span></div>
           </div>
        </div>

        {/* Containers Folder - UPDATED */}
        <div className="flex items-center gap-2 mb-2 mt-4 group"><Folder size={16} className="text-emerald-600"/> <span className="text-emerald-200">containers/</span></div>
        <div className="pl-6 border-l border-slate-800 ml-2 mb-2">
           <div className="flex items-center gap-2"><Folder size={14} className="text-emerald-600"/> <span className="text-emerald-200">Main/</span> <span className="text-xs text-cyan-500/70 border border-cyan-500/20 px-1 rounded">PascalCase</span></div>
           <div className="pl-6 border-l border-slate-800 ml-2 mt-1">
              <div className="flex items-center gap-2 text-slate-300"><FileCode size={14} className="text-blue-400"/> controller.ts</div>
              <div className="flex items-center gap-2 text-amber-300 mt-1"><FileCode size={14} className="text-amber-500"/> index.tsx</div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureTree;