/**
 * @file  src/containers/SalesDashboard/index.tsx
 * @description  pure ui view for the sales dashboard
 *
 * @author ogarcia (ozkary)
 *
 */

import salesDashboardController from './controller';

const SalesDashboard = () => {
  const { data, isLoading, error, refresh } = salesDashboardController();

  if (isLoading && !data) return (
    <div className="flex items-center justify-center h-64 bg-slate-900 rounded-lg border border-slate-800">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
    </div>
  );

  if (error) return (
    <div className="p-6 bg-red-900/20 border border-red-800 rounded-lg text-red-200">
      Error: {error}
      <button onClick={refresh} className="ml-4 underline hover:text-white">Retry</button>
    </div>
  );

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      <div className="bg-slate-950 p-6 border-b border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Global Sales Performance</h2>
          <p className="text-slate-400 text-sm mt-1">Real-time revenue tracking across regions</p>
        </div>
        <button 
          onClick={refresh} 
          className="px-4 py-2 bg-amber-500/10 text-amber-400 border border-amber-500/50 rounded-lg hover:bg-amber-500/20 transition-colors text-sm font-medium flex items-center gap-2"
        >
          <div className={`${isLoading ? 'animate-spin' : ''}`}>
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
          </div>
          {isLoading ? 'Syncing...' : 'Refresh Data'}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6 p-6">
        <div className="col-span-3 bg-gradient-to-r from-cyan-900/20 to-blue-900/20 border border-cyan-800/30 rounded-lg p-6">
          <p className="text-cyan-400 text-sm font-medium uppercase tracking-wider mb-1">Total Revenue</p>
          <div className="text-4xl font-bold text-white">
            {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data?.total || 0)}
          </div>
        </div>
      </div>

      <div className="p-6 pt-0">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-sm">
              <th className="pb-3 font-medium">Region</th>
              <th className="pb-3 font-medium text-right">Revenue</th>
              <th className="pb-3 font-medium text-right">Growth</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data?.regions.map((region) => (
              <tr key={region.id} className="group hover:bg-slate-800/50 transition-colors">
                <td className="py-4 text-slate-200 font-medium">{region.region}</td>
                <td className="py-4 text-right text-slate-300 font-mono">{region.formattedRevenue}</td>
                <td className="py-4 text-right">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-900/30 text-emerald-400 border border-emerald-800">
                    +{region.growth}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SalesDashboard;