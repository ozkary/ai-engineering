import { Mic, MicOff } from "lucide-react";
import type React from "react";
import { useEffect, useRef } from "react";

interface SpeechToTextProps {
  onTranscription: (text: string) => void;
  isListening: boolean;
  onToggleListen: () => void;
  onSessionEnd?: () => void;
}

export const SpeechToText: React.FC<SpeechToTextProps> = ({
  onTranscription,
  isListening,
  onToggleListen,
  onSessionEnd,
}) => {
  const recognitionRef = useRef<any>(null);

  const callbacksRef = useRef({
    onTranscription,
    onToggleListen,
    onSessionEnd,
  });
  const isListeningRef = useRef(isListening);

  // Keep references to state/callbacks fresh without triggering useEffect re-runs
  useEffect(() => {
    callbacksRef.current = { onTranscription, onToggleListen, onSessionEnd };
    isListeningRef.current = isListening;
  });

  useEffect(() => {
    // Check for browser support
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      callbacksRef.current.onTranscription(transcript);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      if (isListeningRef.current && callbacksRef.current.onSessionEnd) {
        callbacksRef.current.onSessionEnd();
      }
    };

    recognition.onend = () => {
      if (isListeningRef.current && callbacksRef.current.onSessionEnd) {
        callbacksRef.current.onSessionEnd();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.abort();
      } catch (err) {
        console.error("Error aborting speech recognition:", err);
      }
    };
  }, []);

  useEffect(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error("Failed to start speech recognition:", err);
      }
    } else {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error("Failed to stop speech recognition:", err);
      }
    }
  }, [isListening]);

  const hasSupport = !!(
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  );

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        type="button"
        disabled={!hasSupport}
        onClick={onToggleListen}
        className={`p-3 rounded-full transition-all duration-300 ${
          !hasSupport
            ? "bg-slate-200 text-slate-400 cursor-not-allowed"
            : isListening
              ? "bg-rose-500 text-white animate-pulse ring-4 ring-rose-300"
              : "bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-800 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        }`}
        title={
          !hasSupport
            ? "Speech-to-text not supported in this browser"
            : isListening
              ? "Stop listening"
              : "Speak answer"
        }
      >
        {isListening ? (
          <Mic className="w-5 h-5" />
        ) : (
          <MicOff className="w-5 h-5" />
        )}
      </button>
      <span className="text-xs text-slate-500 font-medium">
        {isListening ? "Listening..." : "Voice input"}
      </span>
    </div>
  );
};
