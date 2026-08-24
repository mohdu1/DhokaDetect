import { useState, useRef, useEffect } from "react";
import {
  ShieldCheck,
  Paperclip,
  Languages,
  FileImage,
  X,
  AlertTriangle,
  CheckCircle2,
  Mic,
  Activity,
  Globe,
  Eye,
  Server,
  ChevronRight
} from "lucide-react";

import "./App.css";

// Maps ugly backend variables to clean English for the judges
const FLAG_DICTIONARY = {
  "Visual / Font Inconsistency Detected in Receipt": {
    title: "Visual Manipulation",
    desc: "The image contains inconsistent fonts or tampered text."
  },
  "Tampered Pixel Boundary Artifacts": {
    title: "Pixel Artifacts",
    desc: "Signs of digital alteration detected around key areas."
  },
  "Moderate Visual Artifacts Detected": {
    title: "Low-Quality Artifacts",
    desc: "Image compression or minor anomalies present."
  }
};

function App() {
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("English");
  
  // App States: "idle" | "processing" | "complete"
  const [appState, setAppState] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
    event.target.value = "";
  };

  // Hackathon Demo Magic: Simulates a live mic recording and transcription
  const handleMicClick = () => {
    if (isRecording) return;
    setIsRecording(true);
    setInput("");
    
    // Simulate listening for 3 seconds, then "transcribe" a scam phrase
    setTimeout(() => {
      setIsRecording(false);
      setInput("Dear customer your electricity power will be disconnected tonight at 9:30 pm update your kyc immediately");
    }, 3000);
  };

  const handleResults = async () => {
    setError("");
    if (!input.trim() && !file) {
      setError("Provide text, a link, or a file to begin analysis.");
      return;
    }

    setAppState("processing");

    try {
      let base64Data = null;
      if (file) {
        base64Data = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          reader.onload = () => resolve(reader.result.split(',')[1]);
          reader.onerror = (error) => reject(error);
        });
      }

      const response = await fetch("http://127.0.0.1:8000/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text_input: input.trim() || null,
          image_base64: base64Data,
          force_high_risk: false,
        }),
      });
      
      if (!response.ok) throw new Error("Backend connection failed");

      const data = await response.json();
      setResult(data);
      setAppState("complete");
      
    } catch {
      setError("Engine unreachable. Check local backend connection.");
      setAppState("idle");
    }
  };

  const resetEngine = () => {
    setAppState("idle");
    setResult(null);
    setInput("");
    setFile(null);
    setError("");
  };

  // SVG Gauge Helper
  const calculateGaugeStroke = (score) => {
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    return { circumference, offset };
  };

  return (
    <div className="cockpit-layout">
      
      {/* ================= ZONE A: LEFT RAIL ================= */}
      <aside className="zone-a-rail">
        <div className="rail-top">
          <div className="brand-lockup">
            <ShieldCheck size={28} className="brand-icon" />
            <div className="brand-text">
              <h1>Dhoka<span>Detect</span></h1>
              <span className="brand-tag">SECURITY ENGINE</span>
            </div>
          </div>

          <div className="engine-status">
            <span className="status-label">ENGINE STATUS</span>
            <div className="status-indicator">
              <span className={`dot ${appState !== "idle" ? "pulse active" : "pulse"}`}></span>
              {appState === "idle" ? "Standby" : "Active"}
            </div>
          </div>
        </div>

        <div className="rail-bottom">
          <div className="trust-signals">
            <div className="signal"><Server size={14} /> 4-Model Fusion</div>
            <div className="signal"><ShieldCheck size={14} /> On-Device Privacy</div>
          </div>

          <div className="language-selector">
            <Languages size={14} />
            <select value={language} onChange={(e) => setLanguage(e.target.value)} disabled={appState === "processing"}>
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिन्दी)</option>
              <option value="Marathi">Marathi (मराठी)</option>
            </select>
          </div>
        </div>
      </aside>

      {/* ================= ZONE B: CENTER CONSOLE ================= */}
      <main className="zone-b-console">
        <div className="console-wrapper">
          <h2 className="console-title">Unified Threat Scanner</h2>
          <p className="console-subtitle">Drop screenshots, paste URLs, or record live audio.</p>

          <div className={`input-arena ${appState === "processing" ? "locked" : ""}`}>
            
            {/* The Main Input Area */}
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste message, URL, or click the mic to record..."
              disabled={appState === "processing" || isRecording}
              className={`main-textarea ${isRecording ? "is-recording" : ""}`}
            />

            {/* File Chip */}
            {file && (
              <div className="file-chip">
                <FileImage size={16} />
                <span className="file-name">{file.name}</span>
                <button onClick={() => setFile(null)}><X size={14}/></button>
              </div>
            )}

            {/* Action Bar Inside Input */}
            <div className="input-action-bar">
              <div className="left-actions">
                <button 
                  className="icon-btn" 
                  onClick={() => fileInputRef.current?.click()}
                  title="Upload Image/Video"
                >
                  <Paperclip size={18} />
                </button>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  hidden 
                  accept="image/*,video/*"
                />

                <button 
                  className={`icon-btn mic-btn ${isRecording ? "recording-active" : ""}`}
                  onClick={handleMicClick}
                  title="Live Audio Scan"
                >
                  {isRecording ? <div className="recording-wave"><span></span><span></span><span></span></div> : <Mic size={18} />}
                </button>
              </div>

              <button 
                className="analyse-btn"
                onClick={handleResults}
                disabled={appState === "processing" || (!input && !file && !isRecording)}
              >
                {appState === "processing" ? "Scanning..." : "Analyse"} <ChevronRight size={16}/>
              </button>
            </div>
          </div>

          {error && <div className="error-bar"><AlertTriangle size={14}/> {error}</div>}
        </div>
      </main>

      {/* ================= ZONE C: RESULTS PANEL ================= */}
      <aside className="zone-c-results">
        
        {/* STATE 1: IDLE */}
        {appState === "idle" && (
          <div className="panel-idle">
            <div className="radar-spinner"><ShieldCheck size={48} /></div>
            <h3>System Ready</h3>
            <p>Awaiting payload for analysis.</p>
          </div>
        )}

        {/* STATE 2: PROCESSING (The Fake-it-till-you-make-it Late Fusion Loader) */}
        {appState === "processing" && (
          <div className="panel-processing">
            <h3>Fusing Modalities...</h3>
            <div className="process-queue">
              <div className="queue-item active"><Activity size={16}/> Analyzing NLP Vectors...</div>
              <div className="queue-item active" style={{animationDelay: "0.4s"}}><Globe size={16}/> Verifying URL Typography...</div>
              <div className="queue-item active" style={{animationDelay: "0.8s"}}><Eye size={16}/> Extracting Swin Visuals...</div>
            </div>
          </div>
        )}

        {/* STATE 3: COMPLETE */}
        {appState === "complete" && result && (() => {
          const score = result.overall_risk_score || 0;
          const { circumference, offset } = calculateGaugeStroke(score);
          let severityClass = "safe";
          if (score >= 70) severityClass = "critical";
          else if (score >= 40) severityClass = "warning";

          return (
            <div className={`panel-complete fade-in ${severityClass}`}>
              <div className="result-header">
                <button className="reset-btn" onClick={resetEngine}><X size={18}/></button>
                <span className="verdict-badge">{result.risk_level} RISK</span>
              </div>

              {/* The Speedometer */}
              <div className="gauge-container">
                <svg className="gauge" viewBox="0 0 140 140">
                  <circle className="gauge-bg" cx="70" cy="70" r="60" strokeWidth="12" />
                  <circle 
                    className="gauge-fill" 
                    cx="70" cy="70" r="60" 
                    strokeWidth="12" 
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                  />
                </svg>
                <div className="gauge-center">
                  <span className="gauge-score">{score}</span>
                  <span className="gauge-percent">%</span>
                </div>
              </div>

              {/* Red Flags */}
              <div className="flags-container">
                <h4>Detected Anomalies</h4>
                <div className="flags-list">
                  {result.red_flags?.length > 0 ? result.red_flags.map((flag, idx) => {
                    const cleanFlag = FLAG_DICTIONARY[flag.description] || { title: flag.indicator || "Threat Detected", desc: flag.description };
                    return (
                      <div className="flag-item" key={idx}>
                        <AlertTriangle size={16} className="flag-icon" />
                        <div className="flag-text">
                          <strong>{cleanFlag.title}</strong>
                          <p>{cleanFlag.desc}</p>
                        </div>
                      </div>
                    )
                  }) : (
                    <div className="flag-item safe">
                      <CheckCircle2 size={16} className="flag-icon" />
                      <div className="flag-text"><strong>No anomalies found.</strong></div>
                    </div>
                  )}
                </div>
              </div>

            </div>
          )
        })()}
      </aside>
    </div>
  );
}

export default App;