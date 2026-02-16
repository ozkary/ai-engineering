
/**
 * @file  src/components/Boilerplate/Architecture.tsx
 * @description  container component for displaying the architecture details
 *
 * @author ogarcia (ozkary)
 *
 */

import ArchitectureTree from "../../components/ArchitectureTree";

const Architecture = () => {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Vertical Slice Architecture</h2>
          <p className="text-slate-400 mb-6">
            Our architecture treats every feature as a standalone "Vertical Slice". We use strict naming conventions to distinguish between Logic (camelCase) and UI (PascalCase).
          </p>
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
              <h3 className="text-amber-400 font-bold mb-1">PascalCase Folders</h3>
              <p className="text-sm text-slate-400">Used for <span className="text-white">Containers</span> and <span className="text-white">Components</span>. Indicates a "Renderable Context".</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
              <h3 className="text-cyan-400 font-bold mb-1">camelCase Folders/Files</h3>
              <p className="text-sm text-slate-400">Used for <span className="text-white">Services</span> and <span className="text-white">APIs</span>. Indicates "Functional Logic".</p>
            </div>
          </div>
        </div>
        <div>
          <ArchitectureTree />
        </div>
      </div>
    </div>
  );
};

export default Architecture;