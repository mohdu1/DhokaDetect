"""
DhokaDetect - Multilingual Translation Fallback

Offline safety net for indicator explanations.

Supported languages:
    en = English
    hi = Hindi
    mr = Marathi

Every indicator contains:
    title
    explanation
    action
"""


FALLBACK_TRANSLATIONS = {

    # =====================================================
    # URL / DOMAIN INDICATORS
    # =====================================================

    "NO_HTTPS": {
        "en": {
            "title": "Insecure Connection",
            "explanation": (
                "This link does not use HTTPS, so the connection "
                "may not be securely protected."
            ),
            "action": (
                "Do not enter passwords, OTPs, or payment details "
                "on this website."
            ),
        },
        "hi": {
            "title": "असुरक्षित कनेक्शन",
            "explanation": (
                "इस लिंक में HTTPS का उपयोग नहीं हो रहा है, "
                "इसलिए कनेक्शन सुरक्षित रूप से संरक्षित नहीं हो सकता।"
            ),
            "action": (
                "इस वेबसाइट पर पासवर्ड, OTP या भुगतान संबंधी "
                "जानकारी दर्ज न करें।"
            ),
        },
        "mr": {
            "title": "असुरक्षित कनेक्शन",
            "explanation": (
                "या लिंकमध्ये HTTPS वापरलेले नाही, त्यामुळे "
                "कनेक्शन सुरक्षितपणे संरक्षित नसण्याची शक्यता आहे."
            ),
            "action": (
                "या वेबसाइटवर पासवर्ड, OTP किंवा पेमेंटशी "
                "संबंधित माहिती भरू नका."
            ),
        },
    },

    "LONG_URL": {
        "en": {
            "title": "Unusually Long URL",
            "explanation": (
                "The link is unusually long and may contain hidden "
                "or unnecessary parameters often used in suspicious links."
            ),
            "action": (
                "Avoid opening the link unless you can verify its source."
            ),
        },
        "hi": {
            "title": "असामान्य रूप से लंबा लिंक",
            "explanation": (
                "यह लिंक सामान्य से काफी लंबा है और इसमें छिपे हुए "
                "या अनावश्यक पैरामीटर हो सकते हैं, जिनका उपयोग "
                "संदिग्ध लिंक में किया जाता है।"
            ),
            "action": (
                "स्रोत की पुष्टि किए बिना इस लिंक को न खोलें।"
            ),
        },
        "mr": {
            "title": "असामान्यपणे लांब लिंक",
            "explanation": (
                "हा लिंक नेहमीपेक्षा खूप लांब आहे आणि त्यामध्ये "
                "संशयास्पद लिंकसाठी वापरले जाणारे लपवलेले किंवा "
                "अनावश्यक पॅरामीटर्स असू शकतात."
            ),
            "action": (
                "स्रोताची खात्री केल्याशिवाय हा लिंक उघडू नका."
            ),
        },
    },

    "EXCESSIVE_SPECIAL_CHARACTERS": {
        "en": {
            "title": "Unusual URL Structure",
            "explanation": (
                "The URL contains an unusually high number of special "
                "characters, which can be used to make suspicious links "
                "harder to understand."
            ),
            "action": (
                "Check the complete domain carefully before opening the link."
            ),
        },
        "hi": {
            "title": "असामान्य लिंक संरचना",
            "explanation": (
                "इस URL में बहुत अधिक विशेष अक्षर हैं, जिनका उपयोग "
                "संदिग्ध लिंक को समझना कठिन बनाने के लिए किया जा सकता है।"
            ),
            "action": (
                "लिंक खोलने से पहले पूरे डोमेन की सावधानी से जाँच करें।"
            ),
        },
        "mr": {
            "title": "असामान्य लिंक रचना",
            "explanation": (
                "या URL मध्ये असामान्य प्रमाणात विशेष चिन्हे आहेत. "
                "संशयास्पद लिंक समजणे कठीण करण्यासाठी त्यांचा वापर "
                "केला जाऊ शकतो."
            ),
            "action": (
                "लिंक उघडण्यापूर्वी संपूर्ण डोमेन काळजीपूर्वक तपासा."
            ),
        },
    },

    "IP_ADDRESS_URL": {
        "en": {
            "title": "IP Address Used as Website",
            "explanation": (
                "The link uses a numeric IP address instead of a normal "
                "website domain. This can be a warning sign in phishing attempts."
            ),
            "action": (
                "Do not open the link unless the IP address is verified and trusted."
            ),
        },
        "hi": {
            "title": "वेबसाइट के स्थान पर IP पता",
            "explanation": (
                "इस लिंक में सामान्य वेबसाइट डोमेन के बजाय संख्यात्मक "
                "IP पते का उपयोग किया गया है। यह फ़िशिंग प्रयास का संकेत हो सकता है।"
            ),
            "action": (
                "IP पते की पुष्टि और विश्वसनीयता सुनिश्चित किए बिना लिंक न खोलें।"
            ),
        },
        "mr": {
            "title": "वेबसाइटऐवजी IP पत्ता",
            "explanation": (
                "या लिंकमध्ये नेहमीच्या वेबसाइट डोमेनऐवजी संख्यात्मक "
                "IP पत्ता वापरला आहे. हे फिशिंगच्या प्रयत्नाचे संकेत असू शकते."
            ),
            "action": (
                "IP पत्त्याची खात्री करून तो विश्वसनीय असल्याशिवाय लिंक उघडू नका."
            ),
        },
    },

    "SUSPICIOUS_KEYWORD": {
        "en": {
            "title": "Suspicious Keywords",
            "explanation": (
                "The link contains words commonly associated with account "
                "verification, banking, payments, refunds, or other scam attempts."
            ),
            "action": (
                "Verify the website independently before entering any information."
            ),
        },
        "hi": {
            "title": "संदिग्ध शब्द",
            "explanation": (
                "इस लिंक में लॉगिन, सत्यापन, बैंकिंग, भुगतान, रिफंड "
                "या अन्य धोखाधड़ी से जुड़े सामान्य शब्द पाए गए हैं।"
            ),
            "action": (
                "कोई भी जानकारी दर्ज करने से पहले वेबसाइट की स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "संशयास्पद शब्द",
            "explanation": (
                "या लिंकमध्ये लॉगिन, पडताळणी, बँकिंग, पेमेंट, परतावा "
                "किंवा इतर फसवणुकीशी संबंधित सामान्य शब्द आढळले आहेत."
            ),
            "action": (
                "कोणतीही माहिती भरण्यापूर्वी वेबसाइटची स्वतंत्रपणे खात्री करा."
            ),
        },
    },

    "TYPOSQUATTING": {
        "en": {
            "title": "Possible Brand-Impersonating Domain",
            "explanation": (
                "The domain closely resembles a known brand or organization "
                "and may be attempting to imitate its legitimate website."
            ),
            "action": (
                "Do not trust the link based only on the brand name. "
                "Visit the organization's official website directly."
            ),
        },
        "hi": {
            "title": "संभावित नकली ब्रांड डोमेन",
            "explanation": (
                "यह डोमेन किसी प्रसिद्ध ब्रांड या संस्था के असली डोमेन "
                "से मिलता-जुलता है और उसकी नकल करने का प्रयास हो सकता है।"
            ),
            "action": (
                "सिर्फ ब्रांड के नाम के आधार पर लिंक पर भरोसा न करें। "
                "संस्था की आधिकारिक वेबसाइट सीधे खोलें।"
            ),
        },
        "mr": {
            "title": "ब्रँडची नक्कल करणारा संभाव्य डोमेन",
            "explanation": (
                "हा डोमेन एखाद्या ओळखीच्या ब्रँड किंवा संस्थेच्या अधिकृत "
                "डोमेनसारखा दिसतो आणि त्याची नक्कल करण्याचा प्रयत्न असू शकतो."
            ),
            "action": (
                "फक्त ब्रँडचे नाव पाहून लिंकवर विश्वास ठेवू नका. "
                "संस्थेची अधिकृत वेबसाइट थेट उघडा."
            ),
        },
    },

    "SUSPICIOUS_DOMAIN": {
        "en": {
            "title": "Suspicious Domain",
            "explanation": (
                "The website domain has characteristics commonly associated "
                "with phishing or fraudulent websites."
            ),
            "action": (
                "Avoid entering personal, banking, or payment information."
            ),
        },
        "hi": {
            "title": "संदिग्ध डोमेन",
            "explanation": (
                "इस वेबसाइट के डोमेन में फ़िशिंग या धोखाधड़ी वाली "
                "वेबसाइटों से जुड़े संकेत पाए गए हैं।"
            ),
            "action": (
                "अपनी व्यक्तिगत, बैंकिंग या भुगतान संबंधी जानकारी दर्ज न करें।"
            ),
        },
        "mr": {
            "title": "संशयास्पद डोमेन",
            "explanation": (
                "या वेबसाइटच्या डोमेनमध्ये फिशिंग किंवा फसव्या "
                "वेबसाइटशी संबंधित संकेत आढळले आहेत."
            ),
            "action": (
                "वैयक्तिक, बँकिंग किंवा पेमेंटशी संबंधित माहिती भरू नका."
            ),
        },
    },

    # =====================================================
    # SOCIAL ENGINEERING / TEXT
    # =====================================================

    "URGENCY_PRESSURE": {
        "en": {
            "title": "Urgency Pressure",
            "explanation": (
                "The message creates pressure to act immediately, which is "
                "a common social-engineering technique used by scammers."
            ),
            "action": (
                "Slow down and verify the request through an independent trusted source."
            ),
        },
        "hi": {
            "title": "तुरंत कार्रवाई का दबाव",
            "explanation": (
                "इस संदेश में तुरंत कार्रवाई करने का दबाव बनाया जा रहा है। "
                "यह धोखाधड़ी में इस्तेमाल होने वाली एक सामान्य सोशल-इंजीनियरिंग तकनीक है।"
            ),
            "action": (
                "जल्दबाजी न करें और अनुरोध की पुष्टि किसी स्वतंत्र और विश्वसनीय स्रोत से करें।"
            ),
        },
        "mr": {
            "title": "तातडीने कारवाई करण्याचा दबाव",
            "explanation": (
                "या संदेशातून लगेच कारवाई करण्यासाठी दबाव निर्माण केला जात आहे. "
                "फसवणूक करणारे अशा सोशल इंजिनिअरिंग तंत्राचा वापर करतात."
            ),
            "action": (
                "घाई करू नका आणि विनंतीची खात्री स्वतंत्र व विश्वासार्ह स्रोताकडून करा."
            ),
        },
    },

    "ENTITY_IMPERSONATION": {
        "en": {
            "title": "Organization Impersonation",
            "explanation": (
                "The message appears to represent a bank, government organization, "
                "utility provider, or another trusted entity."
            ),
            "action": (
                "Contact the organization using an official phone number or website "
                "instead of the details in the message."
            ),
        },
        "hi": {
            "title": "संस्था होने का दिखावा",
            "explanation": (
                "यह संदेश किसी बैंक, सरकारी संस्था, बिजली सेवा प्रदाता "
                "या अन्य विश्वसनीय संस्था के नाम का इस्तेमाल करता हुआ दिखाई देता है।"
            ),
            "action": (
                "संदेश में दी गई जानकारी के बजाय संस्था के आधिकारिक नंबर "
                "या वेबसाइट से संपर्क करें।"
            ),
        },
        "mr": {
            "title": "संस्थेची बनावट ओळख",
            "explanation": (
                "हा संदेश बँक, सरकारी संस्था, वीज सेवा प्रदाता किंवा इतर "
                "विश्वासार्ह संस्थेचे प्रतिनिधित्व करत असल्याचे भासवतो."
            ),
            "action": (
                "संदेशातील संपर्काऐवजी संस्थेच्या अधिकृत क्रमांकावर "
                "किंवा वेबसाइटवरून संपर्क करा."
            ),
        },
    },

    "FINANCIAL_COERCION": {
        "en": {
            "title": "Financial Pressure",
            "explanation": (
                "The message asks or pressures you to make a payment, "
                "transfer money, share an OTP, or provide financial information."
            ),
            "action": (
                "Do not transfer money or share OTPs or banking credentials "
                "until the request is independently verified."
            ),
        },
        "hi": {
            "title": "पैसों से जुड़ा दबाव",
            "explanation": (
                "संदेश आपसे भुगतान करने, पैसे ट्रांसफर करने, OTP साझा करने "
                "या वित्तीय जानकारी देने के लिए कहता या दबाव डालता है।"
            ),
            "action": (
                "स्वतंत्र रूप से पुष्टि किए बिना पैसे ट्रांसफर या OTP "
                "और बैंकिंग जानकारी साझा न करें।"
            ),
        },
        "mr": {
            "title": "आर्थिक दबाव",
            "explanation": (
                "या संदेशातून पेमेंट करण्यासाठी, पैसे ट्रान्सफर करण्यासाठी, "
                "OTP सांगण्यासाठी किंवा आर्थिक माहिती देण्यासाठी विनंती "
                "किंवा दबाव टाकला जात आहे."
            ),
            "action": (
                "स्वतंत्रपणे खात्री केल्याशिवाय पैसे ट्रान्सफर करू नका "
                "आणि OTP किंवा बँकिंग माहिती शेअर करू नका."
            ),
        },
    },

    "OTP_REQUEST": {
        "en": {
            "title": "OTP Request",
            "explanation": (
                "The message asks for a one-time password. Legitimate organizations "
                "generally do not ask you to disclose your OTP."
            ),
            "action": (
                "Never share an OTP with another person, even if they claim "
                "to be from a bank or government service."
            ),
        },
        "hi": {
            "title": "OTP की मांग",
            "explanation": (
                "इस संदेश में वन-टाइम पासवर्ड मांगा जा रहा है। वैध संस्थाएं "
                "आमतौर पर आपसे OTP साझा करने के लिए नहीं कहती हैं।"
            ),
            "action": (
                "किसी भी व्यक्ति के साथ OTP साझा न करें, चाहे वह बैंक "
                "या सरकारी सेवा से होने का दावा करे।"
            ),
        },
        "mr": {
            "title": "OTP ची मागणी",
            "explanation": (
                "या संदेशात वन-टाइम पासवर्ड मागितला जात आहे. अधिकृत संस्था "
                "सामान्यतः तुमच्याकडून OTP सांगण्यास सांगत नाहीत."
            ),
            "action": (
                "समोरची व्यक्ती बँक किंवा सरकारी सेवेतून असल्याचा दावा "
                "करत असली तरी OTP कधीही शेअर करू नका."
            ),
        },
    },

    "PAYMENT_REQUEST": {
        "en": {
            "title": "Payment Request",
            "explanation": (
                "The message contains a request to make a payment or transfer money."
            ),
            "action": (
                "Verify the recipient and purpose independently before making any payment."
            ),
        },
        "hi": {
            "title": "भुगतान का अनुरोध",
            "explanation": (
                "इस संदेश में भुगतान करने या पैसे ट्रांसफर करने का अनुरोध किया गया है।"
            ),
            "action": (
                "भुगतान करने से पहले प्राप्तकर्ता और भुगतान के उद्देश्य "
                "की स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "पेमेंटची विनंती",
            "explanation": (
                "या संदेशात पेमेंट करण्यासाठी किंवा पैसे ट्रान्सफर करण्यासाठी "
                "विनंती केली आहे."
            ),
            "action": (
                "पेमेंट करण्यापूर्वी प्राप्तकर्ता आणि पेमेंटचा उद्देश "
                "स्वतंत्रपणे तपासा."
            ),
        },
    },

    "REFUND_SCAM": {
        "en": {
            "title": "Possible Refund Scam",
            "explanation": (
                "The message uses a refund or reimbursement claim that may be "
                "intended to make you reveal financial information or send money."
            ),
            "action": (
                "Verify refunds directly through the official organization's app or website."
            ),
        },
        "hi": {
            "title": "संभावित रिफंड धोखाधड़ी",
            "explanation": (
                "संदेश रिफंड या पैसे वापस मिलने का दावा करता है, जिसका उद्देश्य "
                "आपकी वित्तीय जानकारी लेना या आपसे पैसे भेजवाना हो सकता है।"
            ),
            "action": (
                "रिफंड की पुष्टि संस्था के आधिकारिक ऐप या वेबसाइट से सीधे करें।"
            ),
        },
        "mr": {
            "title": "संभाव्य रिफंड फसवणूक",
            "explanation": (
                "या संदेशात रिफंड किंवा पैसे परत मिळण्याचे कारण दिले आहे. "
                "याचा उद्देश आर्थिक माहिती मिळवणे किंवा तुमच्याकडून पैसे पाठवून "
                "घेणे असू शकतो."
            ),
            "action": (
                "रिफंडची खात्री संस्थेच्या अधिकृत ॲप किंवा वेबसाइटवरून थेट करा."
            ),
        },
    },

    "KYC_REQUEST": {
        "en": {
            "title": "KYC Verification Request",
            "explanation": (
                "The message asks you to update or verify KYC information, "
                "which is frequently used in phishing scams."
            ),
            "action": (
                "Complete KYC only through the official bank, wallet, "
                "or service application or website."
            ),
        },
        "hi": {
            "title": "KYC सत्यापन का अनुरोध",
            "explanation": (
                "संदेश आपसे KYC जानकारी अपडेट या सत्यापित करने के लिए कहता है। "
                "ऐसी मांगों का उपयोग अक्सर फ़िशिंग धोखाधड़ी में किया जाता है।"
            ),
            "action": (
                "KYC केवल बैंक, वॉलेट या सेवा के आधिकारिक ऐप "
                "या वेबसाइट के माध्यम से करें।"
            ),
        },
        "mr": {
            "title": "KYC पडताळणीची विनंती",
            "explanation": (
                "या संदेशात KYC माहिती अपडेट किंवा पडताळण्यास सांगितले आहे. "
                "अशा विनंत्यांचा फिशिंग फसवणुकीत वारंवार वापर केला जातो."
            ),
            "action": (
                "KYC फक्त बँक, वॉलेट किंवा सेवेच्या अधिकृत ॲप "
                "किंवा वेबसाइटवरूनच करा."
            ),
        },
    },

    # =====================================================
    # VISUAL INDICATORS
    # =====================================================

    "VISUAL_MANIPULATION": {
        "en": {
            "title": "Possible Visual Manipulation",
            "explanation": (
                "The image contains visual characteristics that may indicate "
                "editing, manipulation, or a forged document or payment proof."
            ),
            "action": (
                "Do not rely on the image alone. Verify the transaction "
                "through the official application or account."
            ),
        },
        "hi": {
            "title": "संभावित दृश्य छेड़छाड़",
            "explanation": (
                "इस तस्वीर में ऐसे दृश्य संकेत हैं जो संपादन, छेड़छाड़ "
                "या नकली दस्तावेज़ अथवा भुगतान प्रमाण की ओर इशारा कर सकते हैं।"
            ),
            "action": (
                "केवल तस्वीर के आधार पर भरोसा न करें। आधिकारिक ऐप "
                "या खाते के माध्यम से लेनदेन की पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "संभाव्य दृश्य फेरफार",
            "explanation": (
                "या प्रतिमेत संपादन, फेरफार किंवा बनावट कागदपत्र "
                "अथवा पेमेंट पुराव्याचे संकेत दिसून येतात."
            ),
            "action": (
                "फक्त प्रतिमेवर विश्वास ठेवू नका. अधिकृत ॲप "
                "किंवा खात्यातून व्यवहाराची खात्री करा."
            ),
        },
    },

    "VISUAL_FONT_INCONSISTENCY": {
        "en": {
            "title": "Font Inconsistency",
            "explanation": (
                "Different fonts, spacing, or text rendering styles may indicate "
                "that parts of the image have been edited or combined."
            ),
            "action": (
                "Treat the document or screenshot as unverified "
                "and confirm it through an official source."
            ),
        },
        "hi": {
            "title": "फ़ॉन्ट में असंगति",
            "explanation": (
                "अलग-अलग फ़ॉन्ट, स्पेसिंग या टेक्स्ट की शैली यह संकेत दे सकती है "
                "कि तस्वीर के कुछ हिस्सों को संपादित या जोड़ा गया है।"
            ),
            "action": (
                "दस्तावेज़ या स्क्रीनशॉट को अप्रमाणित मानें "
                "और आधिकारिक स्रोत से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "फॉन्टमधील विसंगती",
            "explanation": (
                "वेगवेगळे फॉन्ट, अंतर किंवा मजकूर दाखवण्याची शैली "
                "प्रतिमेतील काही भाग संपादित किंवा जोडलेले असल्याचे सूचित करू शकते."
            ),
            "action": (
                "कागदपत्र किंवा स्क्रीनशॉट अप्रमाणित समजा "
                "आणि अधिकृत स्रोताकडून खात्री करा."
            ),
        },
    },

    "SUSPICIOUS_QR_CODE": {
        "en": {
            "title": "Suspicious QR Code",
            "explanation": (
                "The image contains a QR code associated with a potentially "
                "risky payment or redirection request."
            ),
            "action": (
                "Do not scan the QR code unless you have independently verified "
                "who created it and where it leads."
            ),
        },
        "hi": {
            "title": "संदिग्ध QR कोड",
            "explanation": (
                "इस तस्वीर में ऐसा QR कोड है जो संभावित रूप से जोखिमपूर्ण "
                "भुगतान या रीडायरेक्शन अनुरोध से जुड़ा हो सकता है।"
            ),
            "action": (
                "QR कोड को स्कैन करने से पहले यह स्वतंत्र रूप से जांचें "
                "कि इसे किसने बनाया है और यह कहां ले जाता है।"
            ),
        },
        "mr": {
            "title": "संशयास्पद QR कोड",
            "explanation": (
                "या प्रतिमेत संभाव्य धोकादायक पेमेंट किंवा रीडायरेक्शन "
                "विनंतीशी संबंधित QR कोड आढळला आहे."
            ),
            "action": (
                "QR कोड कोणी तयार केला आणि तो कुठे नेतो याची "
                "स्वतंत्रपणे खात्री केल्याशिवाय तो स्कॅन करू नका."
            ),
        },
    },

    # =====================================================
    # AUDIO / VOICE
    # =====================================================

    "SYNTHETIC_VOICE_SIGNAL": {
        "en": {
            "title": "Possible AI-Generated Voice",
            "explanation": (
                "The audio contains characteristics associated with "
                "synthetic or AI-generated speech."
            ),
            "action": (
                "Do not trust payment or account requests based only on the voice. "
                "Verify the person's identity through another channel."
            ),
        },
        "hi": {
            "title": "संभावित AI-निर्मित आवाज़",
            "explanation": (
                "ऑडियो में ऐसे संकेत पाए गए हैं जो कृत्रिम या AI से "
                "बनाए गए भाषण से जुड़े हो सकते हैं।"
            ),
            "action": (
                "केवल आवाज़ के आधार पर भुगतान या खाते से जुड़ी किसी मांग "
                "पर भरोसा न करें। किसी अन्य माध्यम से व्यक्ति की पहचान की पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "संभाव्य AI-निर्मित आवाज",
            "explanation": (
                "ऑडिओमध्ये कृत्रिम किंवा AI द्वारे तयार केलेल्या आवाजाशी "
                "संबंधित संकेत आढळले आहेत."
            ),
            "action": (
                "फक्त आवाजेवर आधारित पेमेंट किंवा खात्याशी संबंधित विनंतीवर "
                "विश्वास ठेवू नका. दुसऱ्या माध्यमातून व्यक्तीची ओळख तपासा."
            ),
        },
    },

    "HUMAN_VOICE_SIGNAL": {
        "en": {
            "title": "Human Voice Signal",
            "explanation": (
                "The audio analysis did not detect the synthetic-voice "
                "characteristics being checked by the model."
            ),
            "action": (
                "A human voice does not prove that the caller is trustworthy. "
                "Verify suspicious requests independently."
            ),
        },
        "hi": {
            "title": "मानवी आवाज़ का संकेत",
            "explanation": (
                "ऑडियो विश्लेषण में मॉडल द्वारा जांचे जा रहे कृत्रिम "
                "आवाज़ के संकेत नहीं मिले।"
            ),
            "action": (
                "मानवीय आवाज़ होने से यह साबित नहीं होता कि कॉल करने वाला "
                "विश्वसनीय है। संदिग्ध अनुरोधों की स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "मानवी आवाजेचा संकेत",
            "explanation": (
                "ऑडिओ विश्लेषणात मॉडेल तपासत असलेले कृत्रिम आवाजाचे "
                "संकेत आढळले नाहीत."
            ),
            "action": (
                "आवाज मानवी आहे याचा अर्थ समोरची व्यक्ती विश्वासार्ह आहे असे "
                "होत नाही. संशयास्पद विनंत्यांची स्वतंत्रपणे खात्री करा."
            ),
        },
    },

    # =====================================================
    # ML / MODEL EVIDENCE
    # =====================================================

    "ML_LEGITIMATE_CONTEXT": {
        "en": {
            "title": "Legitimate Message Pattern",
            "explanation": (
                "The local machine-learning model found patterns that are more "
                "consistent with a normal transactional or informational message "
                "than with a scam."
            ),
            "action": (
                "The message appears low risk, but still verify unexpected links, "
                "payment requests, or sensitive information requests."
            ),
        },
        "hi": {
            "title": "सामान्य संदेश का पैटर्न",
            "explanation": (
                "स्थानीय मशीन-लर्निंग मॉडल ने ऐसे पैटर्न पाए हैं जो धोखाधड़ी वाले "
                "संदेश की तुलना में सामान्य लेनदेन या जानकारी देने वाले संदेश से "
                "अधिक मेल खाते हैं।"
            ),
            "action": (
                "संदेश कम जोखिम वाला दिखाई देता है, लेकिन किसी भी अनपेक्षित लिंक, "
                "भुगतान अनुरोध या संवेदनशील जानकारी की मांग की पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "सामान्य संदेशाचा नमुना",
            "explanation": (
                "स्थानिक मशीन-लर्निंग मॉडेलला फसवणुकीच्या संदेशापेक्षा सामान्य "
                "व्यवहार किंवा माहिती देणाऱ्या संदेशाशी अधिक जुळणारे नमुने आढळले आहेत."
            ),
            "action": (
                "हा संदेश कमी जोखमीचा दिसतो, तरीही अनपेक्षित लिंक, पेमेंटची विनंती "
                "किंवा संवेदनशील माहितीची मागणी असल्यास तिची खात्री करा."
            ),
        },
    },

    "ML_HIGH_SCAM_CONFIDENCE": {
        "en": {
            "title": "High Scam Confidence",
            "explanation": (
                "The local machine-learning model identified patterns that are "
                "strongly associated with scam messages."
            ),
            "action": (
                "Treat the message as high risk and independently verify "
                "the sender and request."
            ),
        },
        "hi": {
            "title": "धोखाधड़ी की उच्च संभावना",
            "explanation": (
                "स्थानीय मशीन-लर्निंग मॉडल ने ऐसे पैटर्न पहचाने हैं जो "
                "धोखाधड़ी वाले संदेशों से काफी जुड़े हुए हैं।"
            ),
            "action": (
                "संदेश को उच्च जोखिम वाला मानें और प्रेषक तथा अनुरोध "
                "की स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "फसवणुकीची उच्च शक्यता",
            "explanation": (
                "स्थानिक मशीन-लर्निंग मॉडेलने फसवणुकीच्या संदेशांशी "
                "मोठ्या प्रमाणात संबंधित नमुने ओळखले आहेत."
            ),
            "action": (
                "हा संदेश उच्च जोखमीचा समजा आणि पाठवणारा तसेच "
                "विनंतीची स्वतंत्रपणे खात्री करा."
            ),
        },
    },

    "ML_SUSPICIOUS_PATTERN": {
        "en": {
            "title": "Suspicious Pattern Detected",
            "explanation": (
                "The machine-learning model identified patterns in the input "
                "that may be associated with scam or spam activity."
            ),
            "action": (
                "Review the message carefully and verify the sender before taking action."
            ),
        },
        "hi": {
            "title": "संदिग्ध पैटर्न मिला",
            "explanation": (
                "मशीन-लर्निंग मॉडल ने इनपुट में ऐसे पैटर्न पहचाने हैं जो "
                "धोखाधड़ी या स्पैम गतिविधि से जुड़े हो सकते हैं।"
            ),
            "action": (
                "संदेश को ध्यान से जांचें और कोई कार्रवाई करने से पहले "
                "प्रेषक की पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "संशयास्पद नमुना आढळला",
            "explanation": (
                "मशीन-लर्निंग मॉडेलने इनपुटमध्ये फसवणूक किंवा स्पॅमशी "
                "संबंधित असू शकणारे नमुने ओळखले आहेत."
            ),
            "action": (
                "संदेश काळजीपूर्वक तपासा आणि कोणतीही कारवाई करण्यापूर्वी "
                "पाठवणाऱ्याची खात्री करा."
            ),
        },
    },

    # =====================================================
    # SERVICE / SYSTEM
    # =====================================================

    "MODEL_UNAVAILABLE": {
        "en": {
            "title": "Detection Model Unavailable",
            "explanation": (
                "The local detection model could not be initialized, "
                "so the model-based analysis may not be available."
            ),
            "action": (
                "Do not treat the absence of a warning as proof that the message is safe."
            ),
        },
        "hi": {
            "title": "डिटेक्शन मॉडल उपलब्ध नहीं है",
            "explanation": (
                "स्थानीय डिटेक्शन मॉडल शुरू नहीं हो सका, इसलिए मॉडल आधारित "
                "विश्लेषण उपलब्ध नहीं हो सकता।"
            ),
            "action": (
                "चेतावनी न मिलने को संदेश के सुरक्षित होने का प्रमाण न मानें।"
            ),
        },
        "mr": {
            "title": "डिटेक्शन मॉडेल उपलब्ध नाही",
            "explanation": (
                "स्थानिक डिटेक्शन मॉडेल सुरू करता आले नाही, त्यामुळे "
                "मॉडेलवर आधारित विश्लेषण उपलब्ध नसण्याची शक्यता आहे."
            ),
            "action": (
                "इशारा मिळाला नाही म्हणजे संदेश सुरक्षित आहे असे समजू नका."
            ),
        },
    },

    "VISION_SERVICE_ERROR": {
        "en": {
            "title": "Visual Analysis Unavailable",
            "explanation": (
                "The visual analysis service could not process the image."
            ),
            "action": (
                "Do not assume the image is safe. Verify the document, "
                "screenshot, or payment proof independently."
            ),
        },
        "hi": {
            "title": "दृश्य विश्लेषण उपलब्ध नहीं है",
            "explanation": (
                "दृश्य विश्लेषण सेवा तस्वीर को संसाधित नहीं कर सकी।"
            ),
            "action": (
                "तस्वीर को सुरक्षित न मानें। दस्तावेज़, स्क्रीनशॉट या "
                "भुगतान प्रमाण की स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "दृश्य विश्लेषण उपलब्ध नाही",
            "explanation": (
                "दृश्य विश्लेषण सेवा प्रतिमेवर प्रक्रिया करू शकली नाही."
            ),
            "action": (
                "प्रतिमा सुरक्षित आहे असे समजू नका. कागदपत्र, स्क्रीनशॉट "
                "किंवा पेमेंट पुराव्याची स्वतंत्रपणे खात्री करा."
            ),
        },
    },

    "AUDIO_SERVICE_ERROR": {
        "en": {
            "title": "Audio Analysis Unavailable",
            "explanation": (
                "The audio analysis service could not process the recording."
            ),
            "action": (
                "Do not assume the caller or recording is safe. "
                "Verify suspicious requests through another channel."
            ),
        },
        "hi": {
            "title": "ऑडियो विश्लेषण उपलब्ध नहीं है",
            "explanation": (
                "ऑडियो विश्लेषण सेवा रिकॉर्डिंग को संसाधित नहीं कर सकी।"
            ),
            "action": (
                "कॉलर या रिकॉर्डिंग को सुरक्षित न मानें। संदिग्ध अनुरोध "
                "की किसी अन्य माध्यम से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "ऑडिओ विश्लेषण उपलब्ध नाही",
            "explanation": (
                "ऑडिओ विश्लेषण सेवा रेकॉर्डिंगवर प्रक्रिया करू शकली नाही."
            ),
            "action": (
                "कॉलर किंवा रेकॉर्डिंग सुरक्षित आहे असे समजू नका. "
                "संशयास्पद विनंतीची दुसऱ्या माध्यमातून खात्री करा."
            ),
        },
    },

    "TEXT_EVALUATION_ERROR": {
        "en": {
            "title": "Text Analysis Error",
            "explanation": (
                "The text analysis component encountered an error "
                "while evaluating the message."
            ),
            "action": (
                "Do not interpret the missing analysis as proof that the message is safe."
            ),
        },
        "hi": {
            "title": "टेक्स्ट विश्लेषण त्रुटि",
            "explanation": (
                "संदेश का विश्लेषण करते समय टेक्स्ट विश्लेषण घटक में त्रुटि हुई।"
            ),
            "action": (
                "विश्लेषण उपलब्ध न होने को संदेश के सुरक्षित होने का प्रमाण न मानें।"
            ),
        },
        "mr": {
            "title": "मजकूर विश्लेषण त्रुटी",
            "explanation": (
                "संदेशाचे विश्लेषण करताना मजकूर विश्लेषण घटकामध्ये त्रुटी आली."
            ),
            "action": (
                "विश्लेषण उपलब्ध नसणे म्हणजे संदेश सुरक्षित आहे असे समजू नका."
            ),
        },
    },

    "MANUAL_OVERRIDE": {
        "en": {
            "title": "Manual Risk Override",
            "explanation": (
                "The risk result was manually elevated for testing "
                "or demonstration purposes."
            ),
            "action": (
                "Do not treat this indicator as evidence from an automated detector."
            ),
        },
        "hi": {
            "title": "मैनुअल जोखिम ओवरराइड",
            "explanation": (
                "परीक्षण या डेमो के उद्देश्य से जोखिम परिणाम को "
                "मैन्युअल रूप से बढ़ाया गया है।"
            ),
            "action": (
                "इसे स्वचालित डिटेक्टर से मिले वास्तविक प्रमाण के रूप में न मानें।"
            ),
        },
        "mr": {
            "title": "मॅन्युअल जोखीम ओव्हरराइड",
            "explanation": (
                "चाचणी किंवा डेमोसाठी जोखीम परिणाम मॅन्युअली वाढवण्यात आला आहे."
            ),
            "action": (
                "हा स्वयंचलित डिटेक्टरकडून मिळालेला वास्तविक पुरावा समजू नका."
            ),
        },
    },

    # =====================================================
    # GENERIC FALLBACK
    # =====================================================

    "UNKNOWN_INDICATOR": {
        "en": {
            "title": "Suspicious Activity Detected",
            "explanation": (
                "The system detected an indicator that does not have "
                "a specific explanation in the offline translation dictionary."
            ),
            "action": (
                "Exercise caution and verify the sender, website, "
                "or request independently."
            ),
        },
        "hi": {
            "title": "संदिग्ध गतिविधि का पता चला",
            "explanation": (
                "सिस्टम ने एक ऐसे संकेत का पता लगाया है जिसकी ऑफलाइन "
                "अनुवाद सूची में विशेष व्याख्या उपलब्ध नहीं है।"
            ),
            "action": (
                "सावधानी बरतें और प्रेषक, वेबसाइट या अनुरोध की "
                "स्वतंत्र रूप से पुष्टि करें।"
            ),
        },
        "mr": {
            "title": "संशयास्पद गतिविधी आढळली",
            "explanation": (
                "सिस्टमने असा संकेत ओळखला आहे ज्याचे विशिष्ट स्पष्टीकरण "
                "ऑफलाइन भाषांतर यादीत उपलब्ध नाही."
            ),
            "action": (
                "सावध राहा आणि पाठवणारा, वेबसाइट किंवा विनंतीची "
                "स्वतंत्रपणे खात्री करा."
            ),
        },
    },
}


# =========================================================
# FALLBACK TRANSLATION FUNCTION
# =========================================================

def get_fallback_translation(
    indicator: str,
    lang: str = "en",
) -> dict:
    """
    Return the offline translation for an indicator.

    Parameters:
        indicator:
            Standard indicator key.

        lang:
            Language code:
                en = English
                hi = Hindi
                mr = Marathi

    Returns:
        Dictionary containing:
            title
            explanation
            action
    """

    if not indicator:
        indicator = "UNKNOWN_INDICATOR"

    indicator = indicator.upper().strip()

    # -----------------------------------------------------
    # Normalize language
    # -----------------------------------------------------

    lang = (lang or "en").lower().strip()

    language_aliases = {
        "english": "en",
        "हिंदी": "hi",
        "hindi": "hi",
        "हिन्दी": "hi",
        "मराठी": "mr",
        "marathi": "mr",
    }

    lang = language_aliases.get(
        lang,
        lang,
    )

    # Unsupported language → English

    if lang not in (
        "en",
        "hi",
        "mr",
    ):
        lang = "en"

    # Unknown indicator → generic fallback

    translation = FALLBACK_TRANSLATIONS.get(
        indicator,
        FALLBACK_TRANSLATIONS[
            "UNKNOWN_INDICATOR"
        ],
    )

    return translation[lang]