/**
 * @file  src/components/Boilerplate/FeatureDemo.tsx
 * @description  container component for the live feature demonstration
 *
 * @author ogarcia (ozkary)
 *
 */

import SalesDashboard from "../../components/SalesDashboard";


const FeatureDemo = () => {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AI Driven Architecture</h1>
        <p className="text-slate-400 text-lg">
          This dashboard is built strictly following the <span className="text-amber-400 font-mono text-sm bg-amber-950/30 px-2 py-0.5 rounded border border-amber-900/50">View → Controller → Service → API</span> pattern.
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Architecture Context Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-lg">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Active Logic</h3>
            <div className="space-y-6 relative">
              <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-slate-800 -z-10"></div>
              {/* V C S A Indicators */}
              {[
                { l: 'V', name: 'View', desc: 'Renders UI only', color: 'amber' },
                { l: 'C', name: 'Controller', desc: 'Manages State', color: 'blue' },
                { l: 'S', name: 'Service', desc: 'Business Logic', color: 'purple' },
                { l: 'A', name: 'API', desc: 'Network Calls', color: 'cyan' }
              ].map((item, idx) => (
                <div key={idx} className="flex gap-3 relative bg-slate-900/50 p-1 rounded-r">
                  <div className={`w-6 h-6 rounded-full bg-${item.color}-500/20 border border-${item.color}-500/50 flex items-center justify-center text-${item.color}-500 z-10 text-xs shadow-[0_0_10px_rgba(0,0,0,0.5)]`}>
                    {item.l}
                  </div>
                  <div>
                    <p className={`text-sm font-medium text-${item.color}-400`}>{item.name}</p>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Demo View */}
        <div className="lg:col-span-3">
           <SalesDashboard />
        </div>
      </div>
    </div>
  );
};

export default FeatureDemo;