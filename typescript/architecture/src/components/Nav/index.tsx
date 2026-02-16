
/**
 * @file  src/components/Boilerplate/Nav.tsx
 * @description  navigation component for the boilerplate app
 *
 * @author ogarcia (ozkary)
 *
 */

import { Layers, Layout, Shield, Terminal } from "lucide-react";

const Nav = ({ activeTab, onTabChange }: { activeTab: string, onTabChange: (id: string) => void }) => {
  return (
    <nav className="border-b border-slate-800 bg-slate-950 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-amber-400 to-amber-600 h-8 w-8 rounded-lg flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-amber-500/20">
            <Shield size={18} />
          </div>
          <span className="font-bold text-lg tracking-tight text-slate-100">AI Governance<span className="text-amber-500"> UI</span></span>
        </div>
        
        <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
          {[
            { id: 'demo', label: 'Feature Demo', icon: Layout },
            { id: 'structure', label: 'Architecture', icon: Layers },
            { id: 'governance', label: 'Governance Files', icon: Terminal }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all
                ${activeTab === tab.id 
                  ? 'bg-slate-800 text-white shadow-sm ring-1 ring-slate-700' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}
              `}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Nav;