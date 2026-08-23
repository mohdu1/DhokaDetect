import { useState } from "react";
import {
  ShieldCheck,
  ArrowUpRight,
  Paperclip,
  Languages,
  FileImage,
  X,
  AlertTriangle,
  CheckCircle2,
  MessageSquareText,
  Link2,
  Image,
  Volume2,
  RotateCcw,
} from "lucide-react";

import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("English");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const languages = [
    {
      value: "English",
      explain: "Explain results in",
    },
    {
      value: "Hindi",
      explain: "परिणाम समझाएँ",
    },
    {
      value: "Marathi",
      explain: "निकाल समजावून सांगा",
    },
  ];

  const selectedLanguage = languages.find(
    (item) => item.value === language
  );

  /* =========================
     FILE UPLOAD
  ========================= */

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }

    event.target.value = "";
  };

  const removeFile = () => {
    setFile(null);
  };

  /* =========================
     ANALYSE
  ========================= */

  const handleResults = async () => {
    setError("");
    setResult(null);

    if (!input.trim() && !file) {
      setError(
        "Please paste a message or link, or upload an image/video."
      );
      return;
    }

    setLoading(true);

    try {
     const response = await fetch(
  "https://f199e2ac4ca25a.lhr.life/api/v1/analyze",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text_input: input.trim(),
      url_confidence: null,
      image_confidence: null,
      audio_confidence: null,
    }),
  }
);
      if (!response.ok) {
        throw new Error(
          `Backend returned status ${response.status}`
        );
      }

      const data = await response.json();

      console.log("Backend response:", data);

      setResult(data);
    } catch (err) {
      console.error("Analysis error:", err);

      setError(
        "Unable to analyse the content. Please check the backend connection."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     NEW ANALYSIS
  ========================= */

  const handleNewAnalysis = () => {
    setResult(null);
    setError("");
    setInput("");
    setFile(null);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  /* =========================
     RISK HELPERS
  ========================= */

  const getRiskInfo = (score, level) => {
    const numericScore = Number(score || 0);

    const percentage = Math.max(
      0,
      Math.min(100, numericScore * 100)
    );

    const normalizedLevel =
      String(level || "").toUpperCase();

    if (
      normalizedLevel.includes("HIGH") ||
      percentage >= 70
    ) {
      return {
        className: "high",
        label: "HIGH RISK",
        percentage,
        message:
          "This content shows strong signs of suspicious or scam-like behaviour.",
      };
    }

    if (
      normalizedLevel.includes("MEDIUM") ||
      normalizedLevel.includes("MODERATE") ||
      percentage >= 40
    ) {
      return {
        className: "medium",
        label: "MEDIUM RISK",
        percentage,
        message:
          "This content contains some warning signs. Proceed carefully.",
      };
    }

    return {
      className: "low",
      label: "LOW RISK",
      percentage,
      message:
        "No major warning signs were detected in this content.",
    };
  };

  /* =========================
     CHANNEL ICON
  ========================= */

  const getChannelIcon = (channel) => {
    const value = String(channel).toLowerCase();

    if (value.includes("text")) {
      return <MessageSquareText size={15} />;
    }

    if (
      value.includes("url") ||
      value.includes("link")
    ) {
      return <Link2 size={15} />;
    }

    if (value.includes("image")) {
      return <Image size={15} />;
    }

    if (value.includes("audio")) {
      return <Volume2 size={15} />;
    }

    return <MessageSquareText size={15} />;
  };

  const getChannelName = (channel) => {
    const value = String(channel).toLowerCase();

    if (value.includes("text")) return "TEXT";
    if (value.includes("url") || value.includes("link")) {
      return "LINK";
    }
    if (value.includes("image")) return "IMAGE";
    if (value.includes("audio")) return "AUDIO";

    return String(channel).toUpperCase();
  };

  return (
    <div className="app">

      {/* ================= NAVBAR ================= */}

      <header className="navbar">
        <div className="nav-container">

          <a href="/" className="brand">

            <div className="brand-icon">
              <ShieldCheck
                size={25}
                strokeWidth={2.2}
              />
            </div>

            <div className="brand-text">

              <div className="brand-name">
                Dhoka<span>Detect</span>
              </div>

              <div className="brand-tagline">
                DIGITAL SAFETY
              </div>

            </div>

          </a>

          <nav className="nav-links">

            <a
              href="#how-it-works"
              className="how-link"
            >
              How it works
            </a>

            <a
              href="#check"
              className="protect-button"
            >
              Get Protected
              <ArrowUpRight size={17} />
            </a>

          </nav>

        </div>
      </header>


      <main>

        {/* ================= MINIMAL HERO ================= */}

        <section className="hero">

          <div className="hero-content">

            <h1>
              Don't get fooled.
            </h1>

            <div className="eyebrow">

              <span className="eyebrow-dot"></span>

              AI-POWERED DIGITAL SAFETY

            </div>

            <p className="hero-description">
              Paste a message or link, or upload a photo or video.
              <br />
              We'll help you understand what's suspicious.
            </p>

          </div>

        </section>


        {/* ================= INPUT SECTION ================= */}

        <section
          className="analysis-section"
          id="check"
        >

          <div className="analysis-container">

            {/* LANGUAGE */}

            <div className="language-row">

              <div className="language-label">

                <Languages size={18} />

                <span>
                  {selectedLanguage.explain}
                </span>

              </div>

              <div className="language-select-wrapper">

                <select
                  value={language}
                  onChange={(event) =>
                    setLanguage(event.target.value)
                  }
                  className="language-select"
                  disabled={loading}
                >

                  <option value="English">
                    English
                  </option>

                  <option value="Hindi">
                    Hindi (हिन्दी)
                  </option>

                  <option value="Marathi">
                    Marathi (मराठी)
                  </option>

                </select>

                <span className="select-arrow">
                  ▾
                </span>

              </div>

            </div>


            {/* INPUT */}

            <div className="universal-input">

              <textarea
                value={input}
                onChange={(event) => {
                  setInput(event.target.value);
                  setError("");
                }}
                placeholder="Paste a suspicious message or link here..."
                className="message-input"
                disabled={loading}
              />

              {file && (
                <div className="uploaded-file">

                  <div className="file-info">

                    <div className="file-icon">
                      <FileImage size={20} />
                    </div>

                    <div>

                      <strong>
                        {file.name}
                      </strong>

                      <span>
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                      </span>

                    </div>

                  </div>

                  <button
                    className="remove-file"
                    onClick={removeFile}
                    type="button"
                    disabled={loading}
                  >
                    <X size={18} />
                  </button>

                </div>
              )}

              <div className="input-footer">

                <label
                  htmlFor="file-upload"
                  className="upload-button"
                >

                  <Paperclip size={18} />

                  <span>
                    Upload photo / video
                  </span>

                </label>

                <input
                  id="file-upload"
                  type="file"
                  accept="image/*,video/*"
                  onChange={handleFileChange}
                  hidden
                  disabled={loading}
                />

                <span className="input-hint">
                  JPG · PNG · JPEG · MP4
                </span>

              </div>

            </div>


            {/* ERROR */}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}


            {/* ANALYSE BUTTON */}

            <button
              className="results-button"
              onClick={handleResults}
              type="button"
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="spinner"></span>
                  <span>Checking...</span>
                </>
              ) : (
                <>
                  <span>
                    {language === "Hindi"
                      ? "परिणाम"
                      : language === "Marathi"
                      ? "निकाल"
                      : "Results"}
                  </span>

                  <ArrowUpRight size={20} />
                </>
              )}

            </button>


            {/* =========================
                RESULT SHOWCASE
            ========================= */}

            {result &&
              !loading &&
              (() => {

                const risk = getRiskInfo(
                  result.final_risk_score,
                  result.risk_level
                );

                const flags =
                  result.aggregated_red_flags || [];

                const channels =
                  result.active_channels || [];

                return (

                  <section
                    className={`result-showcase ${risk.className}`}
                  >

                    {/* RESULT HEADER */}

                    <div className="result-top">

                      <div>

                        <span className="result-kicker">
                          ANALYSIS COMPLETE
                        </span>

                        <h2>
                          Here's what we found.
                        </h2>

                      </div>

                      <div className="result-check">
                        <CheckCircle2 size={21} />
                      </div>

                    </div>


                    {/* RISK CARD */}

                    <div className="risk-card">

                      <div className="risk-card-left">

                        <div className="risk-label">
                          RISK LEVEL
                        </div>

                        <div className="risk-badge">

                          <AlertTriangle size={17} />

                          {risk.label}

                        </div>

                        <p className="risk-message">
                          {risk.message}
                        </p>

                      </div>


                      <div className="risk-score">

                        <div className="score-number">

                          {risk.percentage.toFixed(1)}

                          <span>
                            %
                          </span>

                        </div>

                        <div className="score-label">
                          risk score
                        </div>

                      </div>

                    </div>


                    {/* PROGRESS BAR */}

                    <div className="risk-progress">

                      <div className="progress-header">

                        <span>
                          Overall risk
                        </span>

                        <strong>
                          {risk.percentage.toFixed(1)}%
                        </strong>

                      </div>

                      <div className="progress-track">

                        <div
                          className="progress-fill"
                          style={{
                            width: `${risk.percentage}%`,
                          }}
                        ></div>

                      </div>

                    </div>


                    {/* RED FLAGS */}

                    <div className="result-section">

                      <div className="result-section-heading">

                        <div>

                          <span>
                            WARNING SIGNS
                          </span>

                          <h3>
                            Red flags detected
                          </h3>

                        </div>

                        <div className="flag-count">
                          {flags.length}
                        </div>

                      </div>


                      {flags.length > 0 ? (

                        <div className="flag-list">

                          {flags.map(
                            (flag, index) => (

                              <div
                                className="flag-card"
                                key={index}
                              >

                                <div className="flag-icon">

                                  <AlertTriangle
                                    size={20}
                                  />

                                </div>

                                <div className="flag-content">

                                  <strong>
                                    {flag}
                                  </strong>

                                  <span>
                                    This is a warning sign
                                    that deserves attention.
                                  </span>

                                </div>

                              </div>

                            )
                          )}

                        </div>

                      ) : (

                        <div className="no-flags">

                          <CheckCircle2 size={20} />

                          <span>
                            No specific red flags were
                            identified.
                          </span>

                        </div>

                      )}

                    </div>


                    {/* ACTIVE CHANNELS */}

                    {channels.length > 0 && (

                      <div className="result-section channel-section">

                        <div className="result-section-heading">

                          <div>

                            <span>
                              ANALYSED THROUGH
                            </span>

                            <h3>
                              Active channels
                            </h3>

                          </div>

                        </div>


                        <div className="channel-list">

                          {channels.map(
                            (channel, index) => (

                              <div
                                className="channel-chip"
                                key={index}
                              >

                                {getChannelIcon(channel)}

                                {getChannelName(channel)}

                              </div>

                            )
                          )}

                        </div>

                      </div>

                    )}


                    {/* BOTTOM ACTION */}

                    <div className="result-bottom">

                      <div className="result-tip">

                        <ShieldCheck size={19} />

                        <span>
                          Think twice before taking
                          action on suspicious content.
                        </span>

                      </div>

                      <button
                        className="new-analysis-button"
                        onClick={handleNewAnalysis}
                      >

                        <RotateCcw size={17} />

                        Analyse another

                      </button>

                    </div>

                  </section>

                );

              })()}

          </div>

        </section>


        {/* ================= HOW IT WORKS ================= */}

        <section
          className="how-it-works"
          id="how-it-works"
        >

          <div className="how-container">

            <div className="how-header">

              <span className="small-label">
                HOW IT WORKS
              </span>

              <h2>
                Simple enough
                <br />
                <span>for everyone.</span>
              </h2>

            </div>

            <div className="steps">

              <div className="step">

                <div className="step-number">
                  01
                </div>

                <h3>
                  Give us the suspicious content.
                </h3>

                <p>
                  Paste a message or link, or upload
                  an image or video.
                </p>

              </div>

              <div className="step">

                <div className="step-number">
                  02
                </div>

                <h3>
                  We check the warning signs.
                </h3>

                <p>
                  DhokaDetect looks for suspicious
                  patterns and manipulation indicators.
                </p>

              </div>

              <div className="step">

                <div className="step-number">
                  03
                </div>

                <h3>
                  Understand before you act.
                </h3>

                <p>
                  Get a simple explanation and a safer
                  next step in your chosen language.
                </p>

              </div>

            </div>

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer className="footer">

        <div className="footer-brand">

          <ShieldCheck size={18} />

          DhokaDetect

        </div>

        <span>
          Detect · Explain · Protect.
        </span>

      </footer>

    </div>
  );
}

export default App;