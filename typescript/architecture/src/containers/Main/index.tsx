/**
 * @file  src/components/Boilerplate/Main.tsx
 * @description  main layout container handling tab switching
 *
 * @author ogarcia (ozkary)
 *
 */

import { useState } from "react";
import Nav from "../../components/Nav";
import FeatureDemo from "../FeatureDemo";
import Governance from "../Governance";
import Architecture from "../Architecture";


const Main = () => {
  const [activeTab, setActiveTab] = useState('demo');

  const renderContent = () => {
    switch (activeTab) {
      case 'demo': return <FeatureDemo />;
      case 'structure': return <Architecture />;
      case 'governance': return <Governance />;
      default: return <FeatureDemo />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-amber-500/30">
      <Nav activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-12">
        {renderContent()}
      </main>
    </div>
  );
};

export default Main;