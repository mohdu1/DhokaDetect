import { useEffect, useRef, useState } from "react";
import {
  Paperclip,
  X,
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  Check,
} from "lucide-react";

import "./App.css";


/* =========================================================
   BACKEND API
========================================================= */

const API_URL =
  "http://127.0.0.1:8000/api/v2/analyze/multimodal";


/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {
  English: {
    digitalSafety: "DIGITAL SAFETY",

    title: "Don't get fooled.",
    title2: "Know the Dhoka.",

    subtitle:
      "Paste a message, link, or upload something suspicious.",

    input: "INPUT",

    placeholder:
      "Paste a suspicious message or link here...",

    upload: "Upload photo / video",

    analyse: "Analyse",
    analysing: "Analysing",

    analysisComplete: "ANALYSIS COMPLETE",

    signals: "SIGNALS DETECTED",

    reset: "Reset",

    highRisk: "HIGH RISK",
    mediumRisk: "MEDIUM RISK",
    lowRisk: "LOW RISK",

    action: "ACTION",

    riskScore: "RISK SCORE",

    engine: "ENGINE",
    inputType: "INPUT",

    local: "LOCAL",
    textUrl: "TEXT / URL",
    file: "FILE",
    audioRecord: "VOICE RECORDING",

    noFlags:
      "No specific red flags returned.",

    noFlagsDescription:
      "Continue to verify important requests independently.",

    attention:
      "This deserves your attention.",

    warningFound:
      "Some warning signals were found.",

    noMajorSignals:
      "No major warning signals detected.",

    footer:
      "DETECT · EXPLAIN · PROTECT",

    systemError:
      "Unable to analyse the content. Please check the backend connection.",
  },

  Hindi: {
    digitalSafety: "डिजिटल सुरक्षा",

    title: "धोखे में मत आइए।",
    title2: "धोखा पहचानिए।",

    subtitle:
      "संदेश, लिंक या संदिग्ध फोटो/वीडियो यहाँ डालें।",

    input: "इनपुट",

    placeholder:
      "संदिग्ध संदेश या लिंक यहाँ डालें...",

    upload: "फोटो / वीडियो अपलोड करें",

    analyse: "जाँचें",
    analysing: "जाँच हो रही है",

    analysisComplete: "जाँच पूरी",

    signals: "संदिग्ध संकेत",

    reset: "रीसेट",

    highRisk: "उच्च जोखिम",
    mediumRisk: "मध्यम जोखिम",
    lowRisk: "कम जोखिम",

    action: "क्या करें",

    riskScore: "जोखिम स्कोर",

    engine: "इंजन",
    inputType: "इनपुट",

    local: "लोकल",
    textUrl: "टेक्स्ट / लिंक",
    file: "फाइल",
    audioRecord: "ध्वनि रिकॉर्डिंग",

    noFlags:
      "कोई विशेष संदिग्ध संकेत नहीं मिला।",

    noFlagsDescription:
      "महत्वपूर्ण अनुरोधों को स्वतंत्र रूप से सत्यापित करें।",

    attention:
      "इस पर ध्यान देना जरूरी है।",

    warningFound:
      "कुछ चेतावनी संकेत मिले हैं।",

    noMajorSignals:
      "कोई बड़ा चेतावनी संकेत नहीं मिला।",

    footer:
      "पहचानें · समझें · सुरक्षित रहें",

    systemError:
      "जाँच नहीं हो सकी। कृपया बैकएंड कनेक्शन जाँचें।",
  },

  Marathi: {
    digitalSafety: "डिजिटल सुरक्षा",

    title: "फसवणुकीला बळी पडू नका.",
    title2: "धोका ओळखा.",

    subtitle:
      "संदेश, लिंक किंवा संशयास्पद फोटो/व्हिडिओ येथे टाका.",

    input: "इनपुट",

    placeholder:
      "संशयास्पद संदेश किंवा लिंक येथे टाका...",

    upload: "फोटो / व्हिडिओ अपलोड करा",

    analyse: "तपासा",
    analysing: "तपासणी सुरू",

    analysisComplete: "तपासणी पूर्ण",

    signals: "संशयास्पद संकेत",

    reset: "रीसेट",

    highRisk: "उच्च धोका",
    mediumRisk: "मध्यम धोका",
    lowRisk: "कमी धोका",

    action: "काय करावे",

    riskScore: "जोखीम स्कोअर",

    engine: "इंजिन",
    inputType: "इनपुट",

    local: "लोकल",
    textUrl: "टेक्स्ट / लिंक",
    file: "फाइल",
    audioRecord: "आवाज रेकॉर्डिंग",

    noFlags:
      "कोणतेही विशेष संशयास्पद संकेत आढळले नाहीत.",

    noFlagsDescription:
      "महत्त्वाचे संदेश किंवा विनंत्या स्वतंत्रपणे तपासा.",

    attention:
      "याकडे लक्ष देणे आवश्यक आहे.",

    warningFound:
      "काही धोक्याचे संकेत आढळले आहेत.",

    noMajorSignals:
      "कोणतेही मोठे धोक्याचे संकेत आढळले नाहीत.",

    footer:
      "ओळखा · समजून घ्या · सुरक्षित रहा",

    systemError:
      "तपासणी होऊ शकली नाही. कृपया बॅकएंड कनेक्शन तपासा.",
  },
};


/* =========================================================
   FLAG DICTIONARY
========================================================= */

const FLAG_DICTIONARY = {
  FAKE_URGENCY_PRESSURE_TACTICS_DET: {
    title: "Urgency pressure",

    explanation:
      "The message creates artificial time pressure to make you act quickly.",

    action:
      "Pause and verify the request through an official source before paying or sharing information.",
  },

  URGENCY_PRESSURE: {
    title: "Urgency pressure",

    explanation:
      "The sender is pushing you to act immediately.",

    action:
      "Do not rush. Verify the request independently.",
  },

  NO_HTTPS: {
    title: "Unsecured connection",

    explanation:
      "The link does not use a secure HTTPS connection.",

    action:
      "Avoid entering passwords, OTPs or payment details.",
  },

  SUSPICIOUS_DOMAIN: {
    title: "Suspicious domain",

    explanation:
      "The website address shows characteristics associated with risky domains.",

    action:
      "Do not open the link. Visit the organisation's official website directly.",
  },

  TYPOSQUATTING: {
    title: "Possible fake website",

    explanation:
      "The domain appears designed to resemble a legitimate brand.",

    action:
      "Check the exact domain before entering any information.",
  },

  BRAND_IMPERSONATION: {
    title: "Brand impersonation",

    explanation:
      "The message appears to imitate a known organisation or service.",

    action:
      "Verify the message using the organisation's official contact details.",
  },

  PAYMENT_REQUEST: {
    title: "Payment request",

    explanation:
      "The content asks you to make a payment or transfer money.",

    action:
      "Do not pay until the request has been independently verified.",
  },

  KYC: {
    title: "KYC request",

    explanation:
      "The message asks for identity or account verification.",

    action:
      "Never share OTPs or sensitive documents through an unsolicited link.",
  },

  OTP: {
    title: "OTP request",

    explanation:
      "The content refers to a one-time password or verification code.",

    action:
      "Never share an OTP with another person.",
  },

  FAKE_PAYMENT_RECEIPT: {
    title: "Possible fake payment proof",

    explanation:
      "The payment evidence contains inconsistencies that may indicate manipulation.",

    action:
      "Verify the transaction directly inside your banking or payment app.",
  },

  SUSPICIOUS_LINK: {
    title: "Suspicious link",

    explanation:
      "The submitted content contains a link with potentially risky characteristics.",

    action:
      "Do not click it. Open the official service manually instead.",
  },
};


/* =========================================================
   AUDIO LOGO
========================================================= */

function AudioLogo({ language, recording }) {
  const audioText = {
    English: "AUDIO",
    Hindi: "ऑडियो",
    Marathi: "ऑडिओ",
  };

  return (
    <div className="audio-logo">

      <div className="audio-logo-word">
        {recording ? "RECORDING..." : audioText[language]}
      </div>

      <svg
        className="audio-wave audio-3d"
        viewBox="0 0 300 70"
        fill="none"
        aria-hidden="true"
      >
        <path d="M0 43 C22 43 24 27 40 27 C56 27 58 51 74 51 C90 51 92 17 108 17 C124 17 126 56 142 56 C158 56 160 8 176 8 C192 8 194 58 210 58 C226 58 228 24 244 24 C260 24 264 43 300 43" className="audio-wave-back" />
        <path d="M0 35 C22 35 24 21 40 21 C56 21 58 45 74 45 C90 45 92 11 108 11 C124 11 126 50 142 50 C158 50 160 2 176 2 C192 2 194 52 210 52 C226 52 228 18 244 18 C260 18 264 37 300 37" className="audio-wave-line" />
        <path d="M18 52L34 56M266 50L284 46" className="audio-3d-shadow" />
      </svg>

    </div>
  );
}


/* =========================================================
   VISUAL LOGO
========================================================= */

function VisualLogo({ language, file }) {

  const visualText = {
    English: "IMAGE / VIDEO",
    Hindi: "इमेज / वीडियो",
    Marathi: "प्रतिमा / व्हिडिओ",
  };

  return (
    <div className="visual-logo">

      <div className="visual-word">
        {visualText[language]}
      </div>

      <svg
        className="visual-scan visual-3d"
        viewBox="0 0 120 70"
        fill="none"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="visualFace" x1="30" y1="16" x2="92" y2="55" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#6678ff" stopOpacity="0.95" />
            <stop offset="1" stopColor="#7565d9" stopOpacity="0.38" />
          </linearGradient>
        </defs>
        <path d="M34 23L46 16L88 22L76 30Z" className="visual-3d-top" />
        <path d="M34 23V49L76 57V30Z" fill="url(#visualFace)" className="visual-3d-face" />
        <path d="M76 30L88 22V48L76 57Z" className="visual-3d-side" />
        <path d="M48 28L66 31L66 45L48 42Z" className="visual-3d-screen" />
        <circle cx="57" cy="36" r="4.5" className="scan-dot" />
        <path d="M24 54L38 57M82 61L96 58" className="visual-3d-shadow" />
      </svg>

    </div>
  );
}


/* =========================================================
   FLAG FORMATTER
========================================================= */

function formatFlag(flag) {

  if (!flag) {
    return {
      title: "Suspicious signal",

      explanation:
        "The system detected an unusual pattern.",

      action:
        "Verify the information before taking action.",
    };
  }

  const cleanFlag = String(flag)
    .trim()
    .replace(/^["']|["']$/g, "");

  if (FLAG_DICTIONARY[cleanFlag]) {
    return FLAG_DICTIONARY[cleanFlag];
  }

  const normalized =
    cleanFlag.toUpperCase();

  if (FLAG_DICTIONARY[normalized]) {
    return FLAG_DICTIONARY[normalized];
  }

  return {
    title: cleanFlag
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      ),

    explanation:
      "The detection engine identified a suspicious pattern in the submitted content.",

    action:
      "Verify the information through an official and trusted source before acting.",
  };
}


/* =========================================================
   RISK CLASS
========================================================= */

function getRiskClass(result) {

  const rawRisk =
    result?.risk_level ||
    result?.risk ||
    result?.verdict ||
    "";

  const risk =
    String(rawRisk).toLowerCase();

  if (
    risk.includes("high") ||
    risk.includes("critical") ||
    risk.includes("danger")
  ) {
    return "critical";
  }

  if (
    risk.includes("medium") ||
    risk.includes("warning")
  ) {
    return "warning";
  }

  if (
    risk.includes("low") ||
    risk.includes("safe")
  ) {
    return "safe";
  }

  const score =
    Number(
      result?.risk_score ??
      result?.score ??
      result?.confidence ??
      0
    );

  if (score >= 70) {
    return "critical";
  }

  if (score >= 40) {
    return "warning";
  }

  return "safe";
}


/* =========================================================
   SCORE
========================================================= */

function getScore(result) {

  let score =
    result?.overall_risk_score ??
    result?.risk_score ??
    result?.score ??
    result?.riskScore ??
    result?.confidence ??
    0;

  score = Number(score);

  if (Number.isNaN(score)) {
    return 0;
  }

  if (score <= 1) {
    score *= 100;
  }

  return Math.max(
    0,
    Math.min(
      100,
      Math.round(score)
    )
  );
}


/* =========================================================
   FLAGS
========================================================= */

function getFlags(result) {

  const possibleFlags =
    result?.red_flags ||
    result?.redFlags ||
    result?.flags ||
    result?.evidence ||
    [];

  if (Array.isArray(possibleFlags)) {
    return possibleFlags;
  }

  if (typeof possibleFlags === "string") {
    return [possibleFlags];
  }

  return [];
}


/* =========================================================
   CIPHER SCRAMBLE — LANGUAGE CHANGE TEXT EFFECT
========================================================= */

const CYPHERS = "!<>-_\\/[]{}—=+*^?#0123456789";

function useScramble(text, speed = 22) {
  const [displayText, setDisplayText] = useState(text);
  const firstRender = useRef(true);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      setDisplayText(text);
      return;
    }

    let iteration = 0;
    let interval;

    interval = window.setInterval(() => {
      setDisplayText(
        text
          .split("")
          .map((letter, index) => {
            if (letter === " ") return " ";
            if (index < iteration) return letter;
            return CYPHERS[Math.floor(Math.random() * CYPHERS.length)];
          })
          .join("")
      );

      iteration += 0.9;

      if (iteration >= text.length) {
        window.clearInterval(interval);
        setDisplayText(text);
      }
    }, speed);

    return () => window.clearInterval(interval);
  }, [text, speed]);

  return displayText;
}

function GlitchText({ children, speed = 22, className = "" }) {
  const text = String(children ?? "");
  const scrambled = useScramble(text, speed);

  return (
    <span className={`cipher-text ${className}`}>
      {scrambled}
    </span>
  );
}


/* =========================================================
   APP
========================================================= */

function App() {

  const [input, setInput] =
    useState("");

  const [file, setFile] =
    useState(null);

  // New states for Audio Recording via MediaRecorder
  const [recordedAudioBase64, setRecordedAudioBase64] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [language, setLanguage] =
    useState("English");

  const [languageOpen, setLanguageOpen] =
    useState(false);

  const [languageTransition, setLanguageTransition] =
    useState(false);

  const [languageTransitionTarget, setLanguageTransitionTarget] =
    useState("English");

  const [loading, setLoading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");

  const [recording, setRecording] =
    useState(false);

  const t =
    translations[language];


  /* =======================================================
     FILE
  ======================================================= */

  const handleFileChange =
    (event) => {

      const selectedFile =
        event.target.files?.[0];

      if (!selectedFile) {
        return;
      }

      setFile(selectedFile);
      setError("");
      setResult(null);
    };

  /* =======================================================
     AUDIO RECORDING LOGIC
  ======================================================= */
  const toggleRecording = async () => {
    if (recording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      setRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          const reader = new FileReader();
          reader.readAsDataURL(audioBlob);
          reader.onloadend = () => {
            const b64 = reader.result.toString().split(",")[1];
            setRecordedAudioBase64(b64);
          };
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorderRef.current.start();
        setRecording(true);
        setError("");
      } catch (err) {
        setError("Microphone access denied or unsupported.");
      }
    }
  };


  /* =======================================================
     RESET
  ======================================================= */

  const reset = () => {

    setInput("");
    setFile(null);
    setRecordedAudioBase64(null);
    setResult(null);
    setError("");
    setLoading(false);
    
    if (recording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
  };


  /* =======================================================
     ANALYSE - REAL BACKEND FETCH
  ======================================================= */

  const handleAnalyse = async () => {
    if (!input.trim() && !file && !recordedAudioBase64) {
      setError("Please enter a message, link, file, or voice recording.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      let image_base64 = null;
      let audio_base64 = recordedAudioBase64 || null;

      // Handle file conversion to base64 if a file is present
      if (file) {
        const base64String = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          reader.onload = () => {
            // Strip the metadata prefix (e.g., "data:image/jpeg;base64,")
            const resultString = reader.result.toString();
            resolve(resultString.split(',')[1]);
          };
          reader.onerror = error => reject(error);
        });

        // Fixed video handling inclusion
        if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
          image_base64 = base64String;
        } else if (file.type.startsWith('audio/')) {
          audio_base64 = base64String;
        }
      }

      // Execute the real call to the Python API
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text_input: input.trim() || null,
          image_base64: image_base64,
          audio_base64: audio_base64,
          force_high_risk: false
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      
    } catch (err) {
      console.error("Backend connection failed:", err);
      setError(t.systemError || "Unable to analyse the content. Please check the backend connection.");
    } finally {
      setLoading(false);
    }
  };


  /* =======================================================
     RESULT DATA
  ====================================================== */

  const score =
    result
      ? getScore(result)
      : 0;

  const riskClass =
    result
      ? getRiskClass(result)
      : "safe";

  const flags =
    result
      ? getFlags(result)
      : [];

  const riskLabel =
    riskClass === "critical"
      ? t.highRisk
      : riskClass === "warning"
      ? t.mediumRisk
      : t.lowRisk;


  /* =======================================================
     GAUGE
  ======================================================= */

  const radius = 82;

  const circumference =
    2 * Math.PI * radius;

  const dashOffset =
    circumference -
    (score / 100) *
      circumference;


  return (

    <main className={`app-shell ${languageTransition ? "language-transitioning" : ""}`}>

      <div className="language-glitch-stage" aria-hidden="true">
        <div className="language-glitch-grid" />

        <div className="language-glitch-copy">
          <span className="glitch-copy-back">
            {translations[language].title}
          </span>

          <span className="glitch-copy-main">
            {translations[languageTransitionTarget].title2}
          </span>

          <span className="glitch-copy-slice slice-a">
            {translations[languageTransitionTarget].title2}
          </span>

          <span className="glitch-copy-slice slice-b">
            {translations[languageTransitionTarget].title2}
          </span>
        </div>

        <div className="language-glitch-meta">
          <span>{language === "English" ? "EN" : language === "Hindi" ? "हि" : "म"}</span>
          <i />
          <span>{languageTransitionTarget === "English" ? "EN" : languageTransitionTarget === "Hindi" ? "हि" : "म"}</span>
        </div>

        <span className="language-glitch-bar bar-one" />
        <span className="language-glitch-bar bar-two" />
        <span className="language-glitch-bar bar-three" />
      </div>


      {/* =================================================
         HEADER
      ================================================= */}

      <header className="topbar">

        <div className="brand-lockup">

          <div className="brand-copy">

            <div className="brand-name">
              Dhoka<span>Detect</span>
            </div>

          </div>

        </div>


        <div className="header-center">

          <span className="header-category">
            DIGITAL SAFETY
          </span>

          <span className="header-divider" />

          <span className="header-status">

            <span className="live-dot" />

            ENGINE READY

          </span>

        </div>


        <div className="language-control">

          <span className="language-label">
            Language / भाषा
          </span>

          <div className="language-picker">

            <button
              type="button"
              className={`language-trigger ${
                languageOpen ? "open" : ""
              }`}
              onClick={() =>
                setLanguageOpen((prev) => !prev)
              }
              aria-haspopup="listbox"
              aria-expanded={languageOpen}
            >
              <span className="language-current">
                {language === "English"
                  ? "English"
                  : language === "Hindi"
                  ? "हिन्दी"
                  : "मराठी"}
              </span>

              <ChevronDown
                size={14}
                strokeWidth={1.8}
                className="language-chevron"
              />
            </button>

            {languageOpen && (
              <div
                className="language-menu"
                role="listbox"
                aria-label="Language / भाषा"
              >
                {[
                  ["English", "English", "EN"],
                  ["Hindi", "हिन्दी", "हि"],
                  ["Marathi", "मराठी", "म"],
                ].map(([value, label, code]) => (
                  <button
                    key={value}
                    type="button"
                    className={`language-option ${
                      language === value ? "active" : ""
                    }`}
                    onClick={() => {
                      if (language === value) {
                        setLanguageOpen(false);
                        return;
                      }

                      setLanguageTransitionTarget(value);
                      setLanguageTransition(true);
                      setLanguageOpen(false);

                      // Let the glitch reveal the new language before
                      // the page resolves into its final state.
                      window.setTimeout(() => {
                        setLanguage(value);
                      }, 70);

                      window.setTimeout(() => {
                        setLanguageTransition(false);
                      }, 760);
                    }}
                    role="option"
                    aria-selected={language === value}
                  >
                    <span className="language-code">
                      {code}
                    </span>

                    <span className="language-name">
                      {label}
                    </span>

                    {language === value && (
                      <Check
                        size={14}
                        strokeWidth={2.2}
                        className="language-check"
                      />
                    )}
                  </button>
                ))}
              </div>
            )}

          </div>

        </div>

      </header>


      {/* =================================================
         MAIN
      ================================================= */}

      <section
        className={`main-stage ${
          result
            ? "has-result"
            : ""
        }`}
      >


        {/* =================================================
            INPUT
        ================================================= */}

        {!result && (

          <div className="input-view">

            <div className="hero-copy">

              <h1>

                <GlitchText speed={18}>{t.title}</GlitchText>

                <br />

                <span>
                  <GlitchText speed={18}>{t.title2}</GlitchText>
                </span>

              </h1>


              <p>
                <GlitchText speed={16}>{t.subtitle}</GlitchText>
              </p>

            </div>


            {/* =================================================
                LIVE THREAT FIELD
                Subtle background visualization for the empty
                right side of the single-page dashboard.
            ================================================= */}

            <div className="threat-field" aria-hidden="true">

              <div className="threat-field-header">
                <span className="threat-field-live">
                  <span className="threat-field-dot" />
                  LIVE THREAT FIELD
                </span>

                <span className="threat-field-ready">
                  LOCAL ENGINE · READY
                </span>
              </div>

              <div className="threat-radar">

                <div className="threat-grid-plane" />

                <div className="threat-orbit orbit-outer" />
                <div className="threat-orbit orbit-middle" />
                <div className="threat-orbit orbit-inner" />

                <span className="threat-node node-1" />
                <span className="threat-node node-2" />
                <span className="threat-node node-3" />
                <span className="threat-node node-4" />
                <span className="threat-node node-5" />

                <span className="threat-link link-1" />
                <span className="threat-link link-2" />
                <span className="threat-link link-3" />
                <span className="threat-link link-4" />

                <span className="threat-core">
                  <span className="threat-core-inner" />
                </span>

                <span className="threat-scan-pulse" />

              </div>

              <div className="threat-field-footer">
                <span>TEXT</span>
                <span>URL</span>
                <span>VISION</span>
                <span>AUDIO</span>
              </div>

            </div>


            {/* INPUT ARENA */}

            <div
              className={`input-arena ${
                loading
                  ? "loading"
                  : ""
              }`}
            >

              <div className="input-label">
                {t.input}
              </div>


              {loading && (
                <div className="analysis-scan-overlay" aria-hidden="true">
                  <div className="scan-lens">
                    <div className="scan-lens-glass">
                      <div className="scan-lens-highlight" />
                      <div className="scan-lens-refraction" />
                      <div className="scan-lens-sweep" />
                    </div>
                    <div className="scan-lens-rim rim-outer" />
                    <div className="scan-lens-rim rim-inner" />
                    <div className="scan-lens-handle" />
                    <div className="scan-lens-shadow" />
                  </div>
                </div>
              )}


              <textarea
                className="main-textarea"

                value={input}

                onChange={(e) =>
                  setInput(
                    e.target.value
                  )
                }

                placeholder={
                  t.placeholder
                }

                disabled={loading}
              />


              {/* FILE CHIP - Modified to include audio recording */}

              {(file || recordedAudioBase64) && (

                <div className="file-chip">

                  <Paperclip
                    size={13}
                  />

                  <span>
                    {file ? file.name : "Recorded Voice Note (.wav)"}
                  </span>

                  <button
                    onClick={() => {
                      setFile(null);
                      setRecordedAudioBase64(null);
                    }}

                    disabled={
                      loading
                    }
                  >

                    <X size={13} />

                  </button>

                </div>

              )}


              {/* ACTION BAR */}

              <div className="input-action-bar">


                <div className="left-actions">


                  {/* =================================================
                      IMAGE / VIDEO
                  ================================================= */}

                  <label
                    className={`visual-trigger ${
                      file
                        ? "file-selected"
                        : ""
                    }`}

                    title={
                      t.upload
                    }
                  >

                    <VisualLogo
                      language={
                        language
                      }

                      file={file}
                    />

                    <input
                      type="file"

                      accept="image/*,video/*"

                      onChange={
                        handleFileChange
                      }

                      hidden
                    />

                  </label>


                  {/* =================================================
                      AUDIO
                  ================================================= */}

                  <button
                    className={`audio-trigger ${
                      recording
                        ? "recording-active"
                        : ""
                    }`}

                    onClick={toggleRecording}

                    title="Voice input"
                  >

                    <AudioLogo
                      language={
                        language
                      }
                      recording={recording}
                    />

                  </button>

                </div>


                {/* ANALYSE */}

                <button
                  type="button"
                  className={`analyse-btn ${loading ? "is-loading" : ""}`}
                  onClick={handleAnalyse}
                  disabled={loading}
                  aria-label={t.analyse}
                  aria-busy={loading}
                  title={t.analyse}
                >
                  <span className="analyse-orb" aria-hidden="true">
                    <span className="analyse-orb-glow" />
                    <span className="analyse-ring ring-one" />
                    <span className="analyse-ring ring-two" />
                    <span className="analyse-ring ring-three" />
                    <span className="analyse-lens">
                      <span className="analyse-lens-highlight" />
                    </span>
                    <span className="analyse-scan-line" />
                  </span>

                  <span className="analyse-label">
                    <GlitchText speed={20}>{t.analyse}</GlitchText>
                  </span>
                </button>

              </div>

            </div>


            {/* ERROR */}

            {error && (

              <div className="error-bar">

                <AlertTriangle
                  size={15}
                />

                <span>
                  {error}
                </span>

              </div>

            )}

          </div>

        )}


        {/* =================================================
            RESULTS
        ================================================= */}

        {result && (

          <div className="result-view">


            <div className="result-topline">

              <div>

                <div className="section-number">
                  02 / ANALYSIS
                </div>

                <h2>
                  {t.analysisComplete}
                </h2>

              </div>


              <button
                className="reset-btn"

                onClick={reset}
              >

                <RotateCcw
                  size={15}
                />

                <span>
                  {t.reset}
                </span>

              </button>

            </div>


            {/* RESULT OVERVIEW */}

            <div className="result-overview">


              {/* SCORE */}

              <div
                className={`score-block ${
                  riskClass
                }`}
              >

                <div className="score-label">
                  {t.riskScore}
                </div>


                <div className="gauge">

                  <svg
                    viewBox="0 0 190 190"
                  >

                    <circle
                      className="gauge-track"

                      cx="95"

                      cy="95"

                      r={radius}
                    />


                    <circle
                      className="gauge-progress"

                      cx="95"

                      cy="95"

                      r={radius}

                      style={{
                        strokeDasharray:
                          circumference,

                        strokeDashoffset:
                          dashOffset,
                      }}
                    />

                  </svg>


                  <div className="gauge-content">

                    <strong>
                      {score}
                    </strong>

                    <span>
                      /100
                    </span>

                  </div>

                </div>


                <div className="risk-label">
                  {riskLabel}
                </div>

              </div>


              {/* VERDICT */}

              <div className="verdict-block">

                <div
                  className={`verdict-badge ${
                    riskClass
                  }`}
                >
                  {riskLabel}
                </div>


                <h3>

                  {score >= 70
                    ? t.attention
                    : score >= 40
                    ? t.warningFound
                    : t.noMajorSignals}

                </h3>


                <p>
                  DhokaDetect analysed
                  the available evidence
                  and identified the
                  signals shown below.
                </p>


                <div className="evidence-meta">

                  <div>

                    <span>
                      {t.engine}
                    </span>

                    <strong>
                      {t.local}
                    </strong>

                  </div>


                  <div>

                    <span>
                      {t.inputType}
                    </span>

                    <strong>

                      {file
                        ? t.file
                        : recordedAudioBase64 
                        ? t.audioRecord 
                        : t.textUrl}

                    </strong>

                  </div>

                </div>

              </div>

            </div>


            {/* SIGNALS */}

            <div className="signals-section">

              <div className="signals-heading">

                <span>
                  {t.signals}
                </span>

                <span className="signal-count">
                  {flags.length}
                </span>

              </div>


              {flags.length > 0 ? (

                <div className="flags-grid">

                  {flags
                    .slice(0, 3)
                    .map(
                      (
                        flag,
                        index
                      ) => {

                        const info =
                          typeof flag ===
                          "object"

                            ? {
                                title:
                                  flag.title ||
                                  "Suspicious signal",

                                explanation:
                                  flag.explanation ||
                                  "The system identified a suspicious pattern.",

                                action:
                                  flag.preventive_measure ||
                                  flag.action ||
                                  "Verify before taking action.",
                              }

                            : formatFlag(
                                flag
                              );


                        return (

                          <div
                            className="flag-card"

                            key={`${flag}-${index}`}
                          >

                            <div className="flag-number">

                              0
                              {index + 1}

                            </div>


                            <AlertTriangle
                              className="flag-alert"

                              size={17}
                            />


                            <h4>
                              {info.title}
                            </h4>


                            <p>
                              {info.explanation}
                            </p>


                            <div className="flag-action">

                              <span>
                                <GlitchText speed={20}>{t.action}</GlitchText>
                              </span>

                              {info.action}

                            </div>

                          </div>

                        );
                      }
                    )}

                </div>

              ) : (

                <div className="no-flags">

                  <CheckCircle2
                    size={18}
                  />

                  <div>

                    <strong>
                      {t.noFlags}
                    </strong>

                    <span>
                      {t.noFlagsDescription}
                    </span>

                  </div>

                </div>

              )}

            </div>


            {/* FOOTER */}

            <div className="analysis-footer">

              <span>
                DHOKADETECT ENGINE
              </span>

              <span>
                FASTAPI · NLP · URL · VISION · FUSION
              </span>

              <span>
                {t.footer}
              </span>

            </div>

          </div>

        )}

      </section>

    </main>
  );
}


export default App;