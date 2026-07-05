/**
 * @file  src/components/Boilerplate/FileViewer.tsx
 * @description  helper component to display code with syntax highlighting style
 *
 * @author ogarcia (ozkary)
 *
 */

import { useState } from "react";
import { FileCode, Check, Copy } from 'lucide-react';


const FileViewer = ({ filename, content }: { filename: string, content: string }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-lg overflow-hidden my-4 h-full flex flex-col my-1">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-2 text-sm text-slate-300 font-mono">
          <FileCode size={16} className="text-amber-400" />
          {filename}
        </div>
        <button onClick={handleCopy} className="text-xs flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors">
          {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-4 text-sm text-left text-slate-300 overflow-x-auto font-mono leading-relaxed flex-grow">
        {content}
      </pre>
    </div>
  );
};

export default FileViewer;