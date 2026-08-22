import { useState } from "react";
import {
  ShieldCheck,
  ArrowUpRight,
  Upload,
  MessageSquareText,
  ImagePlus,
  Sparkles,
  Link2,
  AlertTriangle,
  CheckCircle2,
  ScanFace,
  Languages,
} from "lucide-react";

import "./App.css";

function App() {
  const [mode, setMode] = useState("message");
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);

  const modes = [
    {
      id: "message",
      icon: <MessageSquareText size={20} />,
      title: "Scam Message",
      description: "SMS · WhatsApp · Email",
    },
    {
      id: "screenshot",
      icon: <ImagePlus size={20} />,
      title: "Payment / Screenshot",
      description: "Receipt · QR · Payment proof",
    },
    {
      id: "deepfake",
      icon: <ScanFace size={20} />,
      title: "Deepfake / Media",
      description: "AI-generated · Manipulated media",
    },
  ];

  const handleFile = (event) => {
    const selected = event.target.files?.[0];

    if (selected) {
      setFile(selected);
    }
  };

  const selectMode = (selectedMode) => {
    setMode(selectedMode);
    setFile(null);
    setMessage("");
  };

  return (
    <div className="app">

      {/* ================= NAVBAR ================= */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={22} />
          </div>

          <div>
            <div className="brand-name">
              Dhoka<span>Detect</span>
            </div>

            <div className="brand-subtitle">
              DIGITAL SAFETY
            </div>
          </div>
        </div>

        <div className="nav-links">
          <a href="#analyse">Analyse</a>
          <a href="#how">How it works</a>
          <a href="#about">About</a>
        </div>

        <button className="nav-button">
          Get Protected
          <ArrowUpRight size={16} />
        </button>

      </nav>


      {/* ================= HERO ================= */}

      <main>

        <section className="hero">

          <div className="hero-content">

            <div className="eyebrow">
              <span className="eyebrow-dot"></span>
              AI-POWERED DIGITAL SAFETY
            </div>

            <h1>
              Don't get fooled.
              <br />
              <span>Know the Dhoka.</span>
            </h1>

            <p className="hero-description">
              Suspicious message? Payment request? Fake QR?
              Manipulated media? Understand the risk before
              you take the next step.
            </p>

            <div className="hero-actions">

              <a href="#analyse" className="primary-button">
                Analyse something
                <ArrowUpRight size={18} />
              </a>

              <a href="#how" className="secondary-button">
                How it works
              </a>

            </div>

            <div className="trust-line">

              <div className="trust-icons">
                <div>AI</div>
                <div>✓</div>
                <div>भा</div>
              </div>

              <span>
                Explainable · Multimodal · Regional
              </span>

            </div>

          </div>


          {/* HERO VISUAL */}

          <div className="hero-visual">

            <div className="visual-glow"></div>

            <div className="analysis-card">

              <div className="card-top">

                <div className="card-label">
                  <Sparkles size={15} />
                  MULTIMODAL AI
                </div>

                <div className="live">
                  <span></span>
                  READY
                </div>

              </div>


              <div className="media-preview">

                <div className="media-preview-icon">
                  <ScanFace size={27} />
                </div>

                <div>
                  <small>MEDIA AUTHENTICITY</small>

                  <p>
                    Checking for AI-generation
                    and manipulation indicators...
                  </p>
                </div>

              </div>


              <div className="risk-preview">

                <div>
                  <small>INITIAL ASSESSMENT</small>

                  <strong>
                    Review Required
                  </strong>
                </div>

                <div className="risk-score">
                  ?
                </div>

              </div>


              <div className="progress">
                <div></div>
              </div>


              <div className="signal-list">

                <div>
                  <ScanFace size={16} />
                  Face / media signals
                </div>

                <div>
                  <Sparkles size={16} />
                  AI-generation indicators
                </div>

                <div>
                  <CheckCircle2 size={16} />
                  Explainable result
                </div>

              </div>

            </div>


            {/* FLOATING CARDS */}

            <div className="floating-card floating-one">

              <AlertTriangle size={17} />

              <div>
                <strong>Suspicious signal</strong>
                <span>Needs verification</span>
              </div>

            </div>


            <div className="floating-card floating-two">

              <ScanFace size={17} />

              <div>
                <strong>Media analysis</strong>
                <span>AI indicators</span>
              </div>

            </div>


            <div className="floating-card floating-three">

              <ShieldCheck size={18} />

              <div>
                <strong>Stay protected</strong>
                <span>Verify officially</span>
              </div>

            </div>

          </div>

        </section>


        {/* ================= ANALYSIS ================= */}

        <section id="analyse" className="analyse-section">

          <div className="section-heading">

            <div>

              <div className="section-number">
                01 — ANALYSE
              </div>

              <h2>
                Something feels off?
                <br />
                <span>Let's check.</span>
              </h2>

            </div>

            <p>
              Choose what you want to analyse. DhokaDetect
              can work with suspicious messages, payment
              screenshots and potentially manipulated media.
            </p>

          </div>


          {/* ANALYSIS MODES */}

          <div className="mode-grid">

            {modes.map((item) => (

              <button
                key={item.id}
                className={`mode-card ${
                  mode === item.id ? "active" : ""
                }`}
                onClick={() => selectMode(item.id)}
              >

                <div
                  className={`mode-icon ${
                    item.id === "deepfake"
                      ? "deepfake-icon"
                      : item.id === "screenshot"
                      ? "gold"
                      : "teal"
                  }`}
                >
                  {item.icon}
                </div>

                <div className="mode-text">
                  <strong>{item.title}</strong>
                  <span>{item.description}</span>
                </div>

                {mode === item.id && (
                  <div className="selected-dot">
                    ✓
                  </div>
                )}

              </button>

            ))}

          </div>


          {/* MESSAGE MODE */}

          {mode === "message" && (

            <div className="input-card">

              <div className="input-card-heading">

                <div className="input-icon teal">
                  <MessageSquareText size={20} />
                </div>

                <div>
                  <h3>Paste a suspicious message</h3>
                  <span>
                    SMS · WhatsApp · Email · Payment request
                  </span>
                </div>

              </div>


              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Paste the suspicious message here..."
              />

              <div className="input-footer">

                <span>
                  {message.length} characters
                </span>

                {message && (
                  <button onClick={() => setMessage("")}>
                    Clear
                  </button>
                )}

              </div>

            </div>

          )}


          {/* SCREENSHOT MODE */}

          {mode === "screenshot" && (

            <div className="input-card">

              <div className="input-card-heading">

                <div className="input-icon gold">
                  <ImagePlus size={20} />
                </div>

                <div>
                  <h3>Upload payment evidence</h3>
                  <span>
                    Receipt · QR code · Payment screenshot
                  </span>
                </div>

              </div>


              <label className="upload-area">

                <div className="upload-icon">
                  <Upload size={24} />
                </div>

                <strong>
                  {file
                    ? file.name
                    : "Drop or choose a screenshot"}
                </strong>

                <span>
                  PNG, JPG or JPEG
                </span>

                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg"
                  onChange={handleFile}
                />

              </label>

            </div>

          )}


          {/* DEEPFAKE MODE */}

          {mode === "deepfake" && (

            <div className="input-card deepfake-card">

              <div className="input-card-heading">

                <div className="input-icon deepfake">
                  <ScanFace size={20} />
                </div>

                <div>
                  <h3>Check media authenticity</h3>

                  <span>
                    AI-generated · Face manipulation · Synthetic media
                  </span>
                </div>

              </div>


              <label className="upload-area deepfake-upload">

                <div className="upload-icon deepfake-upload-icon">
                  <ScanFace size={25} />
                </div>

                <strong>
                  {file
                    ? file.name
                    : "Upload an image or media file"}
                </strong>

                <span>
                  Look for potential AI-generation and manipulation indicators
                </span>

                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,video/mp4,video/webm"
                  onChange={handleFile}
                />

              </label>


              <div className="deepfake-note">

                <Sparkles size={15} />

                <span>
                  DhokaDetect analyses media for potential
                  manipulation indicators. Results are not
                  treated as absolute proof of authenticity.
                </span>

              </div>

            </div>

          )}


          {/* ANALYSE BUTTON */}

          <div className="analyse-button-wrapper">

            <button className="analyse-button">

              Analyse Risk

              <ArrowUpRight size={19} />

            </button>

            <span>
              Your content is analysed for suspicious patterns
              and risk indicators.
            </span>

          </div>

        </section>


        {/* ================= HOW IT WORKS ================= */}

        <section id="how" className="features-section">

          <div className="section-number">
            02 — WHY DHOKADETECT
          </div>


          <div className="feature-grid">

            <Feature
              number="01"
              title="Explainable AI"
              icon={<Sparkles size={20} />}
              text="Not just a warning. Understand exactly why something looks suspicious."
            />

            <Feature
              number="02"
              title="Multimodal"
              icon={<ScanFace size={20} />}
              text="Analyse messages, payment screenshots and potentially manipulated media."
            />

            <Feature
              number="03"
              title="Regional"
              icon={<Languages size={20} />}
              text="Get clear explanations designed for users beyond technical English."
            />

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer id="about">

        <div className="footer-brand">

          <ShieldCheck size={20} />

          DhokaDetect

        </div>

        <span>
          Detect · Explain · Educate · Protect
        </span>

        <span>
          Prototype · 2026
        </span>

      </footer>

    </div>
  );
}


function Feature({ number, title, icon, text }) {

  return (

    <div className="feature">

      <div className="feature-number">
        {number}
      </div>

      <div className="feature-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

      <ArrowUpRight
        className="feature-arrow"
        size={20}
      />

    </div>

  );
}


export default App;