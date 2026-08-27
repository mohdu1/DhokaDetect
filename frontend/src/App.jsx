import { useEffect, useRef, useState } from "react";
import {
  Paperclip,
  X,
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  Check,
  FileText,
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

    analysedEvidence:
      "DhokaDetect analysed the available evidence and identified the signals shown below.",

    footerEngine: "DHOKADETECT ENGINE",

    footerStack: "FASTAPI · NLP · URL · VISION · FUSION",

    footer:
      "DETECT · EXPLAIN · PROTECT",

    submittedInput: "SUBMITTED INPUT",
    originalEvidence: "ORIGINAL EVIDENCE",
    viewFull: "VIEW FULL",
    noTextSubmitted: "No text submitted.",
    image: "IMAGE",
    video: "VIDEO",
    audio: "AUDIO",
    fileLabel: "FILE",

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

    analysedEvidence:
      "धोकाडिटेक्ट ने उपलब्ध जानकारी की जाँच की और नीचे दिए गए संकेत पाए।",

    footerEngine: "धोकाडिटेक्ट इंजन",

    footerStack: "फास्टएपीआई · एनएलपी · लिंक · विज़न · फ्यूज़न",

    footer:
      "पहचानें · समझें · सुरक्षित रहें",

    submittedInput: "जमा किया गया इनपुट",
    originalEvidence: "मूल सामग्री",
    viewFull: "पूरा देखें",
    noTextSubmitted: "कोई टेक्स्ट जमा नहीं किया गया।",
    image: "छवि",
    video: "वीडियो",
    audio: "ऑडियो",
    fileLabel: "फ़ाइल",

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

    analysedEvidence:
      "धोकाडिटेक्टने उपलब्ध माहितीची तपासणी केली आणि खालील संकेत ओळखले.",

    footerEngine: "धोकाडिटेक्ट इंजिन",

    footerStack: "फास्टएपीआय · एनएलपी · लिंक · व्हिजन · फ्यूजन",

    footer:
      "ओळखा · समजून घ्या · सुरक्षित रहा",

    submittedInput: "सादर केलेले इनपुट",
    originalEvidence: "मूळ सामग्री",
    viewFull: "पूर्ण पहा",
    noTextSubmitted: "कोणताही मजकूर सादर केलेला नाही.",
    image: "प्रतिमा",
    video: "व्हिडिओ",
    audio: "ऑडिओ",
    fileLabel: "फाइल",

    systemError:
      "तपासणी होऊ शकली नाही. कृपया बॅकएंड कनेक्शन तपासा.",
  },
};


/* =========================================================
   FLAG DICTIONARY
========================================================= */

const FLAG_DICTIONARY = {
  FAKE_URGENCY_PRESSURE_TACTICS_DET: {
    English: { title: "Urgency pressure", explanation: "The message creates artificial time pressure to make you act quickly.", action: "Pause and verify the request through an official source before paying or sharing information." },
    Hindi: { title: "Urgency pressure", explanation: "The message creates artificial time pressure to make you act quickly.", action: "Pause and verify the request through an official source before paying or sharing information." },
    Marathi: { title: "Urgency pressure", explanation: "The message creates artificial time pressure to make you act quickly.", action: "Pause and verify the request through an official source before paying or sharing information." },
  },

  URGENCY_PRESSURE: {
    English: { title: "Urgency pressure", explanation: "The sender is pushing you to act immediately.", action: "Do not rush. Verify the request independently." },
    Hindi: { title: "Urgency pressure", explanation: "The sender is pushing you to act immediately.", action: "Do not rush. Verify the request independently." },
    Marathi: { title: "Urgency pressure", explanation: "The sender is pushing you to act immediately.", action: "Do not rush. Verify the request independently." },
  },

  NO_HTTPS: {
    English: { title: "Unsecured connection", explanation: "The link does not use a secure HTTPS connection.", action: "Avoid entering passwords, OTPs or payment details." },
    Hindi: { title: "Unsecured connection", explanation: "The link does not use a secure HTTPS connection.", action: "Avoid entering passwords, OTPs or payment details." },
    Marathi: { title: "Unsecured connection", explanation: "The link does not use a secure HTTPS connection.", action: "Avoid entering passwords, OTPs or payment details." },
  },

  SUSPICIOUS_DOMAIN: {
    English: { title: "Suspicious domain", explanation: "The website address shows characteristics associated with risky domains.", action: "Do not open the link. Visit the organisation's official website directly." },
    Hindi: { title: "Suspicious domain", explanation: "The website address shows characteristics associated with risky domains.", action: "Do not open the link. Visit the organisation's official website directly." },
    Marathi: { title: "Suspicious domain", explanation: "The website address shows characteristics associated with risky domains.", action: "Do not open the link. Visit the organisation's official website directly." },
  },

  TYPOSQUATTING: {
    English: { title: "Possible fake website", explanation: "The domain appears designed to resemble a legitimate brand.", action: "Check the exact domain before entering any information." },
    Hindi: { title: "Possible fake website", explanation: "The domain appears designed to resemble a legitimate brand.", action: "Check the exact domain before entering any information." },
    Marathi: { title: "Possible fake website", explanation: "The domain appears designed to resemble a legitimate brand.", action: "Check the exact domain before entering any information." },
  },

  BRAND_IMPERSONATION: {
    English: { title: "Brand impersonation", explanation: "The message appears to imitate a known organisation or service.", action: "Verify the message using the organisation's official contact details." },
    Hindi: { title: "Brand impersonation", explanation: "The message appears to imitate a known organisation or service.", action: "Verify the message using the organisation's official contact details." },
    Marathi: { title: "Brand impersonation", explanation: "The message appears to imitate a known organisation or service.", action: "Verify the message using the organisation's official contact details." },
  },

  PAYMENT_REQUEST: {
    English: {
      title: "Payment request",
      explanation: "The content asks you to make a payment or transfer money.",
      action: "Do not pay until the request has been independently verified.",
    },
    Hindi: {
      title: "भुगतान अनुरोध",
      explanation: "संदेश आपसे भुगतान या पैसे भेजने के लिए कहता है।",
      action: "स्वतंत्र रूप से सत्यापित किए बिना भुगतान न करें।",
    },
    Marathi: {
      title: "पेमेंटची विनंती",
      explanation: "संदेश तुम्हाला पेमेंट किंवा पैसे पाठवण्यास सांगतो.",
      action: "स्वतंत्रपणे पडताळणी केल्याशिवाय पेमेंट करू नका.",
    },
  },

  KYC: {
    English: { title: "KYC request", explanation: "The message asks for identity or account verification.", action: "Never share OTPs or sensitive documents through an unsolicited link." },
    Hindi: { title: "KYC request", explanation: "The message asks for identity or account verification.", action: "Never share OTPs or sensitive documents through an unsolicited link." },
    Marathi: { title: "KYC request", explanation: "The message asks for identity or account verification.", action: "Never share OTPs or sensitive documents through an unsolicited link." },
  },

  OTP: {
    English: {
      title: "OTP request",
      explanation: "The content refers to a one-time password or verification code.",
      action: "Never share an OTP with another person.",
    },
    Hindi: {
      title: "OTP का अनुरोध",
      explanation: "संदेश वन-टाइम पासवर्ड या सत्यापन कोड का उल्लेख करता है।",
      action: "किसी अन्य व्यक्ति के साथ OTP साझा न करें।",
    },
    Marathi: {
      title: "OTP ची विनंती",
      explanation: "संदेश वन-टाइम पासवर्ड किंवा पडताळणी कोडचा उल्लेख करतो.",
      action: "OTP कधीही दुसऱ्या व्यक्तीसोबत शेअर करू नका.",
    },
  },

  FAKE_PAYMENT_RECEIPT: {
    English: { title: "Possible fake payment proof", explanation: "The payment evidence contains inconsistencies that may indicate manipulation.", action: "Verify the transaction directly inside your banking or payment app." },
    Hindi: { title: "Possible fake payment proof", explanation: "The payment evidence contains inconsistencies that may indicate manipulation.", action: "Verify the transaction directly inside your banking or payment app." },
    Marathi: { title: "Possible fake payment proof", explanation: "The payment evidence contains inconsistencies that may indicate manipulation.", action: "Verify the transaction directly inside your banking or payment app." },
  },

  SUSPICIOUS_LINK: {
    English: {
      title: "Suspicious link",
      explanation: "The submitted content contains a link with potentially risky characteristics.",
      action: "Do not click it. Open the official service manually instead.",
    },
    Hindi: {
      title: "संदिग्ध लिंक",
      explanation: "सामग्री में संभावित रूप से जोखिम वाला लिंक है।",
      action: "लिंक पर क्लिक न करें। आधिकारिक सेवा स्वयं खोलें।",
    },
    Marathi: {
      title: "संशयास्पद लिंक",
      explanation: "सामग्रीमध्ये संभाव्य धोकादायक लिंक आहे.",
      action: "लिंकवर क्लिक करू नका. अधिकृत सेवा स्वतः उघडा.",
    },
  },

  URGENT_ACTION_REQUEST: {
    English: { title: "Urgent action request", explanation: "The message combines pressure with a request to act.", action: "Pause and verify the sender through an official channel." },
    Hindi: { title: "तुरंत कार्रवाई का अनुरोध", explanation: "संदेश दबाव बनाकर आपसे कार्रवाई करने को कहता है।", action: "रुकें और आधिकारिक माध्यम से भेजने वाले की पुष्टि करें।" },
    Marathi: { title: "तातडीच्या कृतीची विनंती", explanation: "संदेश दबाव टाकून तुम्हाला कृती करण्यास सांगतो.", action: "थांबा आणि अधिकृत माध्यमातून पाठवणाऱ्याची पडताळणी करा." },
  },

  OTP_PIN_REQUEST: {
    English: { title: "OTP or PIN request", explanation: "The content asks for a one-time password or PIN.", action: "Never share an OTP or PIN with anyone." },
    Hindi: { title: "OTP या PIN का अनुरोध", explanation: "सामग्री वन-टाइम पासवर्ड या PIN माँगती है।", action: "OTP या PIN किसी के साथ साझा न करें।" },
    Marathi: { title: "OTP किंवा PIN ची विनंती", explanation: "सामग्री वन-टाइम पासवर्ड किंवा PIN मागते.", action: "OTP किंवा PIN कोणासोबतही शेअर करू नका." },
  },

  SENSITIVE_INFORMATION_REQUEST: {
    English: { title: "Sensitive information request", explanation: "The message asks for personal, identity, or account information.", action: "Do not share sensitive details until the request is independently verified." },
    Hindi: { title: "संवेदनशील जानकारी का अनुरोध", explanation: "संदेश व्यक्तिगत, पहचान या खाते की जानकारी माँगता है।", action: "स्वतंत्र पुष्टि के बिना संवेदनशील जानकारी साझा न करें।" },
    Marathi: { title: "संवेदनशील माहितीची विनंती", explanation: "संदेश वैयक्तिक, ओळख किंवा खात्याची माहिती मागतो.", action: "स्वतंत्र पडताळणीशिवाय संवेदनशील माहिती शेअर करू नका." },
  },

  SUSPICIOUS_OR_UNOFFICIAL_LINK_DETECTED: {
    English: { title: "Suspicious or unofficial link", explanation: "The content contains a link that may not belong to the claimed service.", action: "Do not open it. Visit the official website manually." },
    Hindi: { title: "संदिग्ध या अनधिकृत लिंक", explanation: "सामग्री में ऐसी लिंक है जो बताए गए संगठन की नहीं हो सकती।", action: "इसे न खोलें। आधिकारिक वेबसाइट स्वयं खोलें।" },
    Marathi: { title: "संशयास्पद किंवा अनधिकृत लिंक", explanation: "सामग्रीमध्ये सांगितलेल्या सेवेशी संबंधित नसलेली लिंक असू शकते.", action: "लिंक उघडू नका. अधिकृत वेबसाइट स्वतः उघडा." },
  },

  URGENT_PAYMENT_REQUEST_DETECTED: {
    English: { title: "Urgent payment request", explanation: "The message pressures you to make a payment quickly.", action: "Do not pay until the request is independently verified." },
    Hindi: { title: "तुरंत भुगतान का अनुरोध", explanation: "संदेश आपसे जल्दी भुगतान करने का दबाव बनाता है।", action: "स्वतंत्र पुष्टि के बिना भुगतान न करें।" },
    Marathi: { title: "तातडीच्या पेमेंटची विनंती", explanation: "संदेश तुमच्यावर लवकर पेमेंट करण्यासाठी दबाव टाकतो.", action: "स्वतंत्र पडताळणीशिवाय पेमेंट करू नका." },
  },

  HUMAN_VOICE_SIGNAL: {
    English: { title: "Human voice signal", explanation: "The recording was analyzed and no synthetic-voice anomaly was detected.", action: "This is an informational result, not a guarantee of identity or safety." },
    Hindi: { title: "मानवी आवाज का संकेत", explanation: "रिकॉर्डिंग की जाँच हुई और कृत्रिम आवाज़ की कोई असामान्यता नहीं मिली।", action: "यह केवल जानकारी है, पहचान या सुरक्षा की गारंटी नहीं।" },
    Marathi: { title: "मानवी आवाजेचा संकेत", explanation: "रेकॉर्डिंगची तपासणी झाली आणि कृत्रिम आवाजाची असामान्यता आढळली नाही.", action: "हा माहितीपर निकाल आहे; ओळख किंवा सुरक्षिततेची हमी नाही." },
  },

  AI_SYNTHETIC_VOICE_FLAGGED: {
    English: { title: "Possible synthetic voice", explanation: "The audio contains patterns associated with an AI-generated voice.", action: "Treat requests from this recording cautiously and verify the speaker independently." },
    Hindi: { title: "संभावित कृत्रिम आवाज", explanation: "ऑडियो में AI-निर्मित आवाज़ से जुड़े पैटर्न मिले हैं।", action: "इस रिकॉर्डिंग के अनुरोधों में सावधानी बरतें और बोलने वाले की स्वतंत्र पुष्टि करें।" },
    Marathi: { title: "संभाव्य कृत्रिम आवाज", explanation: "ऑडिओमध्ये AI-निर्मित आवाजाशी संबंधित नमुने आढळले.", action: "या रेकॉर्डिंगमधील विनंत्यांबाबत सावध रहा आणि बोलणाऱ्याची स्वतंत्र पडताळणी करा." },
  },

  VISUAL_FONT_INCONSISTENCY_DETECTED_IN_RECEIPT: {
    English: { title: "Receipt font inconsistency", explanation: "The receipt contains visual inconsistencies that may indicate editing.", action: "Verify the transaction inside your banking or payment app." },
    Hindi: { title: "रसीद के फ़ॉन्ट में असंगति", explanation: "रसीद में दृश्य असंगतियाँ हैं जो संपादन का संकेत दे सकती हैं।", action: "बैंकिंग या भुगतान ऐप में लेनदेन की पुष्टि करें।" },
    Marathi: { title: "पावतीच्या फॉन्टमध्ये विसंगती", explanation: "पावतीमध्ये संपादन दर्शवणाऱ्या दृश्य विसंगती आढळतात.", action: "बँकिंग किंवा पेमेंट ॲपमध्ये व्यवहाराची पडताळणी करा." },
  },

  TAMPERED_PIXEL_BOUNDARY_ARTIFACTS: {
    English: { title: "Receipt pixel artifacts", explanation: "Pixel boundaries in the receipt may indicate image manipulation.", action: "Verify the transaction directly in the official payment app." },
    Hindi: { title: "रसीद में पिक्सेल असंगतियाँ", explanation: "रसीद की पिक्सेल सीमाएँ छेड़छाड़ का संकेत दे सकती हैं।", action: "आधिकारिक भुगतान ऐप में लेनदेन की पुष्टि करें।" },
    Marathi: { title: "पावतीतील पिक्सेल विसंगती", explanation: "पावतीच्या पिक्सेल सीमा छेडछाडीचा संकेत देऊ शकतात.", action: "अधिकृत पेमेंट ॲपमध्ये व्यवहाराची थेट पडताळणी करा." },
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

function VisualLogo({ language }) {

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

function formatFlag(flag, language = "English") {

  const genericCopy = {
    English: {
      title: "Suspicious signal",
      explanation: "The detection engine identified an unusual pattern in the submitted content.",
      action: "Verify the information through an official and trusted source before acting.",
    },
    Hindi: {
      title: "संदिग्ध संकेत",
      explanation: "जाँच इंजन ने भेजी गई सामग्री में एक असामान्य पैटर्न पाया।",
      action: "कार्रवाई करने से पहले आधिकारिक और विश्वसनीय स्रोत से जानकारी की पुष्टि करें।",
    },
    Marathi: {
      title: "संशयास्पद संकेत",
      explanation: "तपासणी इंजिनने सादर केलेल्या सामग्रीमध्ये असामान्य नमुना ओळखला.",
      action: "कृती करण्यापूर्वी अधिकृत आणि विश्वसनीय स्रोताकडून माहितीची पडताळणी करा.",
    },
  };

  if (!flag) {
    return genericCopy[language] || genericCopy.English;
  }

  const cleanFlag = String(flag)
    .trim()
    .replace(/^['"]|['"]$/g, "")
    .replace(/\s*\(Evidence:.*$/i, "")
    .trim();

  const normalized =
    cleanFlag.toUpperCase();

  if (normalized) {
    for (const key of Object.keys(FLAG_DICTIONARY)) {
      const normalizedKey = key.toUpperCase();

      if (
        normalized.includes(normalizedKey) ||
        normalizedKey.includes(normalized)
      ) {
        const entry = FLAG_DICTIONARY[key];
        return entry[language] || entry;
      }
    }
  }

  return genericCopy[language] || genericCopy.English;
}


/* =========================================================
   RISK CLASS
========================================================= */

function getRiskClass(result) {
  const score = getScore(result);

  if (score >= 60) {
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

  const [submittedPreviewOpen, setSubmittedPreviewOpen] =
    useState(false);

  const [filePreviewUrl, setFilePreviewUrl] =
    useState(null);

  const [showPreview, setShowPreview] =
    useState(false);

  const t =
    translations[language];

  useEffect(() => {
    if (!file) {
      setFilePreviewUrl(null);
      return;
    }

    const url = URL.createObjectURL(file);
    setFilePreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  const togglePreview = () => {
    setShowPreview((prev) => !prev);
  };


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
      setShowPreview(false);
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
      } catch {
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
    setSubmittedPreviewOpen(false);
    setShowPreview(false);
    
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


              {/* ATTACHED FILE / AUDIO CHIP + PREVIEW */}

              {(file || recordedAudioBase64) && (
                <div
                  className="media-attachment-container"
                  style={{ margin: "10px 0" }}
                >
                  <div
                    onClick={togglePreview}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        togglePreview();
                      }
                    }}
                    style={{
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "7px",
                      padding: "7px 11px",
                      background: "rgba(255, 255, 255, 0.06)",
                      border: "1px solid rgba(242, 241, 237, 0.13)",
                      borderRadius: "15px",
                      color: "#ddddda",
                      fontSize: "9px",
                      maxWidth: "80%",
                    }}
                    title="Click to view attachment"
                  >
                    <Paperclip size={13} />

                    <span
                      style={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {file ? file.name : "Recorded Voice Note (.wav)"}
                    </span>

                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        setFile(null);
                        setRecordedAudioBase64(null);
                        setShowPreview(false);
                      }}
                      disabled={loading}
                      aria-label="Remove attachment"
                      style={{
                        display: "flex",
                        border: "none",
                        background: "transparent",
                        color: "var(--muted)",
                        cursor: loading ? "default" : "pointer",
                        padding: 0,
                      }}
                    >
                      <X size={13} />
                    </button>
                  </div>

                  {showPreview && (
                    <div
                      className="media-preview"
                      style={{
                        marginTop: "10px",
                        padding: "10px",
                        border: "1px solid rgba(242, 241, 237, 0.13)",
                        borderRadius: "5px",
                        background: "rgba(255, 255, 255, 0.025)",
                      }}
                    >
                      {file &&
                        file.type.startsWith("image/") &&
                        filePreviewUrl && (
                          <img
                            src={filePreviewUrl}
                            alt="Preview"
                            style={{
                              maxWidth: "100%",
                              maxHeight: "300px",
                              display: "block",
                              objectFit: "contain",
                            }}
                          />
                        )}

                      {file &&
                        file.type.startsWith("video/") &&
                        filePreviewUrl && (
                          <video
                            controls
                            playsInline
                            src={filePreviewUrl}
                            style={{
                              maxWidth: "100%",
                              maxHeight: "300px",
                              display: "block",
                            }}
                          />
                        )}

                      {file &&
                        file.type.startsWith("audio/") &&
                        filePreviewUrl && (
                          <audio
                            controls
                            src={filePreviewUrl}
                            style={{
                              display: "block",
                              width: "100%",
                            }}
                          />
                        )}

                      {recordedAudioBase64 && !file && (
                        <audio
                          controls
                          src={`data:audio/wav;base64,${recordedAudioBase64}`}
                          style={{
                            display: "block",
                            width: "100%",
                          }}
                        />
                      )}
                    </div>
                  )}
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


                <p>{t.analysedEvidence}</p>


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


              {/* SUBMITTED INPUT */}

              <div className="submitted-input-block">

                <div className="submitted-input-heading">
                  <span>{t.submittedInput}</span>
                  <span className="submitted-input-type">
                    {file
                      ? file.type.startsWith("image/")
                        ? "IMAGE"
                        : file.type.startsWith("video/")
                        ? "VIDEO"
                        : file.type.startsWith("audio/")
                        ? "AUDIO"
                        : "FILE"
                      : recordedAudioBase64
                      ? "AUDIO"
                      : "TEXT / URL"}
                  </span>
                </div>

                <div
                  className={`submitted-input-preview ${
                    file ? "has-file" : ""
                  }`}
                >
                  {file && file.type.startsWith("image/") && filePreviewUrl ? (
                    <img
                      src={filePreviewUrl}
                      alt={t.submittedInput}
                    />
                  ) : file && file.type.startsWith("video/") && filePreviewUrl ? (
                    <video
                      src={filePreviewUrl}
                      muted
                      playsInline
                      preload="metadata"
                    />
                  ) : file && file.type.startsWith("audio/") && filePreviewUrl ? (
                    <div className="submitted-audio-preview">
                      <div className="submitted-audio-bars" aria-hidden="true">
                        {Array.from({ length: 18 }).map((_, index) => (
                          <span
                            key={index}
                            style={{
                              height: `${12 + ((index * 17) % 25)}px`,
                            }}
                          />
                        ))}
                      </div>
                      <audio
                        src={filePreviewUrl}
                        controls
                      />
                    </div>
                  ) : recordedAudioBase64 ? (
                    <div className="submitted-audio-preview">
                      <div className="submitted-audio-bars" aria-hidden="true">
                        {Array.from({ length: 18 }).map((_, index) => (
                          <span
                            key={index}
                            style={{
                              height: `${12 + ((index * 17) % 25)}px`,
                            }}
                          />
                        ))}
                      </div>
                      <audio
                        src={`data:audio/wav;base64,${recordedAudioBase64}`}
                        controls
                      />
                    </div>
                  ) : (
                    <div className="submitted-text-preview">
                      <FileText
                        size={16}
                        strokeWidth={1.4}
                      />
                      <p>
                        {input.trim() || t.noTextSubmitted}
                      </p>
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  className="submitted-view-btn"
                  onClick={() => setSubmittedPreviewOpen(true)}
                >
                  <span>{t.viewFull}</span>

                </button>

              </div>

            </div>


            {/* FULL SUBMITTED INPUT MODAL */}

            {submittedPreviewOpen && (
              <div
                className="submitted-modal-backdrop"
                onClick={() => setSubmittedPreviewOpen(false)}
              >
                <div
                  className="submitted-modal"
                  onClick={(event) => event.stopPropagation()}
                >
                  <div className="submitted-modal-header">
                    <div>
                      <span>{t.submittedInput}</span>
                      <strong>ORIGINAL EVIDENCE</strong>
                    </div>

                    <button
                      type="button"
                      onClick={() => setSubmittedPreviewOpen(false)}
                      aria-label={t.reset}
                    >
                      <X size={16} strokeWidth={1.7} />
                    </button>
                  </div>

                  <div className="submitted-modal-content">
                    {file && file.type.startsWith("image/") && filePreviewUrl ? (
                      <img
                        src={filePreviewUrl}
                        alt={t.originalEvidence}
                      />
                    ) : file && file.type.startsWith("video/") && filePreviewUrl ? (
                      <video
                        src={filePreviewUrl}
                        controls
                        playsInline
                      />
                    ) : file && file.type.startsWith("audio/") && filePreviewUrl ? (
                      <audio
                        src={filePreviewUrl}
                        controls
                      />
                    ) : recordedAudioBase64 ? (
                      <audio
                        src={`data:audio/wav;base64,${recordedAudioBase64}`}
                        controls
                      />
                    ) : (
                      <div className="submitted-full-text">
                        {input.trim() || t.noTextSubmitted}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}


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
                    .map(
                      (
                        flag,
                        index
                      ) => {

                        const backendFlag =
                          flag && typeof flag === "object"
                            ? flag
                            : null;

                        const baseIndicator = String(
                          backendFlag?.indicator ||
                          (typeof flag === "string" ? flag : "")
                        ).replace(/\s*\(Evidence:.*$/i, "").trim();

                        const info = formatFlag(baseIndicator, language);
                        const isInformational = baseIndicator === "HUMAN_VOICE_SIGNAL";


                        return (

                          <div
                            className={`flag-card ${isInformational ? "informational" : ""}`}

                            key={`${flag}-${index}`}
                          >

                            <div className="flag-number">

                              0
                              {index + 1}

                            </div>


                            {isInformational ? (
                              <CheckCircle2 className="flag-alert" size={17} />
                            ) : (
                              <AlertTriangle className="flag-alert" size={17} />
                            )}


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
                {t.footerEngine}
              </span>

              <span>
                {t.footerStack}
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