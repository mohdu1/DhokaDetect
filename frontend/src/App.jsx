import { useState } from "react";
import {
  ShieldCheck,
  ArrowUpRight,
  Paperclip,
  Languages,
  FileImage,
  X,
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
      label: "English",
      explain: "Explain results in",
    },
    {
      value: "Hindi",
      label: "Hindi (हिन्दी)",
      explain: "परिणाम समझाएँ",
    },
    {
      value: "Marathi",
      label: "Marathi (मराठी)",
      explain: "निकाल समजावून सांगा",
    },
  ];

  const selectedLanguage = languages.find(
    (item) => item.value === language
  );

  // ================= FILE UPLOAD =================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }

    // Allows selecting the same file again
    event.target.value = "";
  };

  // ================= REMOVE FILE =================

  const removeFile = () => {
    setFile(null);
  };

  // ================= ANALYSE / RESULTS =================

  const handleResults = async () => {
    // Clear previous state
    setError("");
    setResult(null);

    // Validate input
    if (!input.trim() && !file) {
      setError(
        "Please paste a message or link, or upload an image/video."
      );
      return;
    }

    setLoading(true);

    try {
      // Create multipart form data
      const formData = new FormData();

      // Add text if available
      if (input.trim()) {
        formData.append("text", input);
      }

      // Add uploaded file if available
      if (file) {
        formData.append("image", file);
      }

      // Add selected language
      formData.append("language", language);

      console.log("Sending request to backend...");
      console.log("Language:", language);
      console.log("Text:", input);
      console.log("File:", file);

      // Send request to FastAPI
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      // Check HTTP status
      if (!response.ok) {
        throw new Error(
          `Backend returned status ${response.status}`
        );
      }

      // Convert response to JSON
      const data = await response.json();

      console.log("Backend response:", data);

      // Store backend result
      setResult(data);

    } catch (err) {
      console.error("Analysis error:", err);

      setError(
        "Unable to analyse the content. Please make sure the backend is running."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* ================= NAVBAR ================= */}

      <header className="navbar">

        <div className="nav-container">

          {/* BRAND */}

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


          {/* NAVIGATION */}

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


      {/* ================= MAIN ================= */}

      <main>

        {/* ================= HERO ================= */}

        <section className="hero">

          <div className="hero-content">

            <div className="eyebrow">

              <span className="eyebrow-dot"></span>

              AI-POWERED DIGITAL SAFETY

            </div>


            <h1>

              Don't get fooled.

              <br />

              <span>
                Know the Dhoka.
              </span>

            </h1>


            <p className="hero-description">

              Paste a message or link, or upload a photo or video.

              <br />

              We'll help you understand what's suspicious.

            </p>

          </div>

        </section>


        {/* ================= UNIVERSAL INPUT ================= */}

        <section
          className="analysis-section"
          id="check"
        >

          <div className="analysis-container">

            {/* HEADING */}

            <div className="analysis-heading">

              <span className="small-label">
                CHECK SOMETHING SUSPICIOUS
              </span>

              <h2>

                Give us anything

                <br />

                <span>
                  that feels wrong.
                </span>

              </h2>

              <p>

                You don't need to know what type of scam it is.
                Just paste it or upload it — DhokaDetect will
                figure out what to check.

              </p>

            </div>


            {/* ================= LANGUAGE ================= */}

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


            {/* ================= INPUT BOX ================= */}

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


              {/* ================= FILE ================= */}

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

                        {(
                          file.size /
                          (1024 * 1024)
                        ).toFixed(2)}{" "}
                        MB

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


              {/* ================= INPUT FOOTER ================= */}

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


            {/* ================= ERROR ================= */}

            {error && (

              <div className="error-message">

                {error}

              </div>

            )}


            {/* ================= RESULTS BUTTON ================= */}

            <button
              className="results-button"
              onClick={handleResults}
              type="button"
              disabled={loading}
            >

              {loading ? (

                <>
                  <span className="spinner"></span>

                  <span>
                    Checking...
                  </span>
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


            {/* ================= LOADING MESSAGE ================= */}

            {loading && (

              <p className="privacy-note">

                Checking your content for suspicious
                patterns...

              </p>

            )}


            {/* ================= BACKEND RESULT ================= */}

            {result && !loading && (

              <div className="result-box">

                <h3>
                  Analysis Result
                </h3>

                <pre>
                  {JSON.stringify(
                    result,
                    null,
                    2
                  )}
                </pre>

              </div>

            )}


            {!result && !loading && !error && (

              <p className="privacy-note">

                Your content is checked for suspicious
                patterns, links and manipulation indicators.

              </p>

            )}

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

                <span>
                  for everyone.
                </span>

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