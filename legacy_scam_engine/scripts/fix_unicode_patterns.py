from pathlib import Path
import shutil

TARGET = Path("backend/ml_services/model_manager.py")
BACKUP = Path("backend/ml_services/model_manager_before_unicode_fix.py")

if not TARGET.exists():
    raise FileNotFoundError(f"Target file not found: {TARGET}")

# Create backup
shutil.copy2(TARGET, BACKUP)

text = TARGET.read_text(encoding="utf-8")

# Mojibake -> correct Unicode
replacements = {
    # Hindi
    "à¤¤à¥à¤°à¤‚à¤¤": "तुरंत",
    "à¤œà¤²à¥à¤¦à¥€": "जल्दी",
    "à¤…à¤à¥€": "अभी",
    "à¤˜à¤‚à¤Ÿà¥‡": "घंटे",
    "à¤®à¤¿à¤¨à¤Ÿ": "मिनट",

    "à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ": "अकाउंट",
    "à¤¬à¥à¤²à¥‰à¤•": "ब्लॉक",
    "à¤¬à¤‚à¤¦": "बंद",
    "à¤–à¤¾à¤¤à¤¾": "खाता",
    "à¤¹à¥‹": "हो",
    "à¤œà¤¾à¤à¤—à¤¾": "जाएगा",
    "à¤¹à¥ˆ": "है",

    "à¤†à¤§à¤¾à¤°": "आधार",
    "à¤ªà¥ˆà¤¨": "पैन",
    "à¤•à¤¾à¤°à¥à¤¡": "कार्ड",
    "à¤¨à¤‚à¤¬à¤°": "नंबर",
    "à¤µà¤¿à¤µà¤°à¤£": "विवरण",
    "à¤¬à¥ˆà¤‚à¤•": "बैंक",

    "à¤¦à¤°à¥à¤œ": "दर्ज",
    "à¤¡à¤¾à¤²à¥‡à¤‚": "डालें",
    "à¤¡à¤¾à¤²à¥‹": "डालो",
    "à¤¶à¥‡à¤¯à¤°": "शेयर",
    "à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ": "वेरिफाई",
    "à¤¦à¥‡à¤‚": "दें",
    "à¤¦à¥à¤¯à¤¾": "दया",

    "à¤•à¥à¤²à¤¿à¤•": "क्लिक",
    "à¤•à¤°à¥‡à¤‚": "करें",
    "à¤…à¤ªà¤¡à¥‡à¤Ÿ": "अपडेट",
    "à¤ªà¥à¤·à¥à¤Ÿà¤¿": "पुष्टि",

    "à¤à¥à¤—à¤¤à¤¾à¤¨": "भुगतान",
    "à¤ªà¥ˆà¤¸à¥‡": "पैसे",
    "à¤à¥‡à¤œ": "भेज",
    "à¤¶à¥à¤²à¥à¤•": "शुल्क",

    "à¤°à¤¿à¤«à¤‚à¤¡": "रिफंड",
    "à¤µà¤¾à¤ªà¤¸à¥€": "वापसी",

    # Marathi
    "à¤¤à¤¾à¤¤à¥à¤•à¤¾à¤³": "तात्काळ",
    "à¤²à¤—à¥‡à¤š": "लगेच",
    "à¤¤à¥à¤µà¤°à¤¿à¤¤": "त्वरित",

    "à¤–à¤¾à¤¤à¥‡": "खाते",
    "à¤¬à¤‚à¤¦": "बंद",
    "à¤¹à¥‹à¤ˆà¤²": "होईल",
    "à¤¹à¥‹à¤£à¤¾à¤°": "होणार",

    "à¤ªà¤°à¤¤à¤¾à¤µà¤¾": "परतावा",
    "à¤®à¤¿à¤³": "मिळ",
    "à¤®à¤¿à¤³à¤µà¤£à¥à¤¯à¤¾à¤¸à¤¾à¤ à¥€": "मिळवण्यासाठी",

    "à¤ªà¤¾à¤ à¤µà¤¾": "पाठवा",
    "à¤à¤°à¤¾": "करा",
    "à¤¦à¥à¤¯à¤¾": "द्या",

    # Currency
    "â‚¹": "₹",
}

changed = 0

for old, new in replacements.items():
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        changed += count

TARGET.write_text(text, encoding="utf-8")

print("=" * 60)
print("DhokaDetect Unicode Pattern Repair")
print("=" * 60)
print(f"Backup created: {BACKUP}")
print(f"Replacements made: {changed}")
print("Unicode repair completed.")