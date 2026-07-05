/**
 * @file  src/components/Boilerplate/Governance.tsx
 * @description  container component for displaying the governance file contents
 *
 * @author ogarcia (ozkary)
 *
 */

import FileViewer from "../../components/FileViewer";
import { GOVERNANCE_FILES } from "./model";

const Governance = () => {

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
       <div className="grid grid-cols-1 justify-between mb-8">
         <div>
            <h2 className="text-2xl font-bold text-white">Repository Configuration</h2>
            <p className="text-slate-400">These files "program" Copilot to enforce the architecture.</p>
         </div>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
             <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">1. The System Prompt</h3>
             <FileViewer filename=".github/copilot-instructions.md" content={GOVERNANCE_FILES.global} />
          </div>
          <div>
             <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">2. The Scaffolder</h3>
             <FileViewer filename=".github/prompts/new-module.md" content={GOVERNANCE_FILES.scaffold} />
          </div>
          <div className="my-8">
             <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">3. View Guardrails</h3>
             <FileViewer filename=".github/instructions/view-layer.md" content={GOVERNANCE_FILES.viewLayer} />
          </div>
          <div className="my-8">
             <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">4. Controller Guardrails</h3>
             <FileViewer filename=".github/instructions/controller-layer.md" content={GOVERNANCE_FILES.controllerLayer} />
          </div>
       </div>
    </div>
  );
};

export default Governance;