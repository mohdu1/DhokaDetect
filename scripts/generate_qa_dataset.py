import csv
import random
import re
from pathlib import Path
from faker import Faker

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 42
TOTAL_ROWS = 5000

random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

OUTPUT_DIR = Path("datasets")
OUTPUT_FILE = OUTPUT_DIR / "dhokadetect_qa_5000.csv"

# ---------------------------------------------------------
# Indian entities
# ---------------------------------------------------------

BANKS = [
    "SBI",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Kotak Bank",
    "Punjab National Bank",
]

BRANDS = [
    "SBI",
    "HDFC",
    "ICICI",
    "Axis",
    "Paytm",
    "PhonePe",
    "Google Pay",
    "Amazon",
    "Flipkart",
]

REGIONS = [
    "Maharashtra",
    "Karnataka",
    "Delhi",
    "Gujarat",
    "Tamil Nadu",
    "Telangana",
    "West Bengal",
    "Uttar Pradesh",
    "Rajasthan",
]

LANGUAGES = [
    "english",
    "hindi",
    "hinglish",
    "marathi",
]

# ---------------------------------------------------------
# URL generation
# ---------------------------------------------------------

SPOOFED_URL_TEMPLATES = [
    "http://{brand}-kyc-update.in",
    "http://{brand}-verify-account.in",
    "http://{brand}-secure-login.in",
    "https://{brand}-kyc-update.in",
    "https://{brand}-account-verify.co.in",
    "https://{brand}-rewardz.co.in",
    "https://{brand}-refund-claim.in",
    "http://secure-{brand}-verification.com",
    "https://{brand}-customer-care.in",
    "http://{brand}-payment-confirm.in",
]

LEGITIMATE_URLS = [
    "https://www.sbi.co.in",
    "https://www.hdfcbank.com",
    "https://www.icicibank.com",
    "https://www.axisbank.com",
    "https://www.uidai.gov.in",
    "https://www.amazon.in",
    "https://www.flipkart.com",
]

# Deliberately imperfect spellings for typosquatting tests.
TYPOSQUAT_BRANDS = {
    "SBI": [
        "sbi",
        "sbl",
        "sb1",
        "sbiindia",
        "sbi-secure",
    ],
    "HDFC": [
        "hdfc",
        "hdfcb",
        "hdfcsecure",
        "hdfc-bank",
    ],
    "ICICI": [
        "icici",
        "icicibank",
        "icic1",
        "icici-secure",
    ],
    "Axis": [
        "axis",
        "ax1s",
        "axisbank",
        "axis-secure",
    ],
}

# ---------------------------------------------------------
# Message components
# ---------------------------------------------------------

URGENCY = [
    "URGENT!",
    "ACTION REQUIRED!",
    "IMPORTANT NOTICE!",
    "FINAL WARNING!",
    "Respond immediately.",
    "Act within 2 hours.",
    "Complete verification today.",
    "Do not ignore this message.",
]

THREATS = [
    "your account will be blocked",
    "your account will be suspended",
    "your wallet will be permanently blocked",
    "your mobile number will be disconnected",
    "your FASTag will be suspended",
    "your electricity connection will be disconnected",
    "your payment will be cancelled",
]

SENSITIVE_REQUESTS = [
    "share your OTP",
    "enter your OTP",
    "provide your Aadhaar number",
    "provide your PAN details",
    "enter your UPI PIN",
    "share your card details",
    "confirm your bank account details",
]

PAYMENT_REQUESTS = [
    "pay ₹299 as verification charges",
    "pay ₹499 processing fees",
    "pay ₹89 delivery charges",
    "pay ₹1,247 immediately",
    "pay ₹2,499 to activate the service",
]

# ---------------------------------------------------------
# Scam templates
# ---------------------------------------------------------

def kyc_scam():
    bank = random.choice(BANKS)
    url = random.choice(SPOOFED_URL_TEMPLATES).format(
        brand=random.choice(
            TYPOSQUAT_BRANDS.get(bank.split()[0], [bank.lower()])
        )
    )

    text = (
        f"{random.choice(URGENCY)} "
        f"Your {bank} account KYC is incomplete and {random.choice(THREATS)}. "
        f"{random.choice(SENSITIVE_REQUESTS)} using the link below. "
        f"Verify immediately to avoid account suspension. {url}"
    )

    return text, url, "kyc_scam"


def upi_scam():
    amount = random.choice(["₹850", "₹1,250", "₹5,000", "₹18,500"])

    url = random.choice(SPOOFED_URL_TEMPLATES).format(
        brand=random.choice(["upi", "paytm", "phonepe", "gpay"])
    )

    text = (
        f"Your UPI refund of {amount} is pending. "
        f"To receive the refund, {random.choice(SENSITIVE_REQUESTS)} "
        f"through the verification link. {url}"
    )

    return text, url, "upi_scam"


def prize_scam():
    prize = random.choice(["₹10,000", "₹25,00,000", "₹5,00,000"])

    text = (
        f"Congratulations! You have won {prize} in a lucky draw. "
        f"To claim your prize, {random.choice(PAYMENT_REQUESTS)} "
        f"and send the payment confirmation immediately."
    )

    return text, None, "prize_scam"


def electricity_scam():
    url = random.choice([
        "https://msedcl-bill-update.in",
        "https://mahadiscom-payment.in",
        "http://electricity-bill-verification.in",
        "https://maha-vitaran-secure.in",
    ])

    text = (
        f"{random.choice(URGENCY)} "
        f"Your electricity bill is overdue. "
        f"Your connection will be disconnected tonight. "
        f"{random.choice(PAYMENT_REQUESTS)} through the link below. "
        f"{url}"
    )

    return text, url, "electricity_scam"


def delivery_scam():
    url = random.choice([
        "https://amazon-delivery-update.in",
        "https://flipkart-address-verify.in",
        "https://parcel-customs-charge.in",
        "http://courier-address-update.in",
    ])

    text = (
        "Your parcel is currently on hold because of an address issue. "
        f"{random.choice(PAYMENT_REQUESTS)} within 30 minutes "
        f"to prevent the parcel from being returned. {url}"
    )

    return text, url, "delivery_scam"


def loan_scam():
    url = random.choice([
        "https://instant-loan-approval.in",
        "https://quickloan-verification.in",
        "http://personal-loan-confirm.in",
    ])

    text = (
        f"You are eligible for an instant personal loan of "
        f"{random.choice(['₹2,00,000', '₹5,00,000', '₹10,00,000'])}. "
        f"{random.choice(PAYMENT_REQUESTS)}. "
        f"Then provide Aadhaar and PAN details. {url}"
    )

    return text, url, "loan_scam"


def telecom_scam():
    text = (
        f"{random.choice(URGENCY)} "
        "Your mobile KYC is incomplete and your number will be disconnected "
        "within 24 hours. Call customer care and share your OTP to reactivate "
        "the service."
    )

    return text, None, "sim_swap_scam"


def government_scam():
    url = "https://government-benefit-registration.in"

    text = (
        "Congratulations! You have been selected for a government benefit. "
        f"To receive the amount, {random.choice(PAYMENT_REQUESTS)} "
        f"and provide your Aadhaar and bank account details. {url}"
    )

    return text, url, "government_benefit_scam"


# ---------------------------------------------------------
# Regional language templates
# ---------------------------------------------------------

def hindi_scam():
    url = random.choice(SPOOFED_URL_TEMPLATES).format(
        brand=random.choice(["sbi", "hdfc", "paytm", "upi"])
    )

    templates = [
        "आपका बैंक खाता 24 घंटे में बंद हो जाएगा। KYC तुरंत अपडेट करें।",
        "आपका KYC पूरा नहीं हुआ है। खाता बंद होने से बचाने के लिए लिंक पर क्लिक करें।",
        "आपका अकाउंट ब्लॉक होने वाला है। तुरंत OTP से वेरिफाई करें।",
        "आपका रिफंड प्राप्त करने के लिए UPI PIN और OTP दर्ज करें।",
    ]

    text = random.choice(templates) + " " + url

    return text, url, "regional_hindi_scam"


def marathi_scam():
    url = random.choice([
        "https://sbi-kyc-update.in",
        "https://mahadiscom-payment.in",
        "https://upi-refund-verify.in",
    ])

    templates = [
        "तुमचे बँक खाते KYC पूर्ण न झाल्यामुळे बंद होणार आहे. त्वरित KYC अपडेट करा.",
        "तुमचे खाते 24 तासांत ब्लॉक होईल. खालील लिंकवर क्लिक करून पडताळणी करा.",
        "तुमचा वीज बिल भरणा बाकी आहे. आज रात्री वीज कनेक्शन बंद केले जाईल.",
        "रिफंड मिळवण्यासाठी तुमचा OTP आणि UPI PIN द्या.",
    ]

    text = random.choice(templates) + " " + url

    return text, url, "regional_marathi_scam"


def hinglish_scam():
    url = random.choice([
        "https://sbi-kyc-update.in",
        "https://paytm-verify-account.in",
        "https://upi-refund-check.in",
    ])

    templates = [
        "Aapka bank account 24 hours mein block ho jayega. KYC abhi update karo.",
        "Aapka KYC pending hai, warna khaata band ho jayega. Link pe click karo.",
        "Bijli bill pending hai. Aaj raat connection cut ho jayega, abhi payment karo.",
        "Refund receive karne ke liye OTP aur UPI PIN share karo.",
        "Aapko reward mila hai, processing fee pay karke claim karo.",
    ]

    text = random.choice(templates) + " " + url

    return text, url, "regional_hinglish_scam"


# ---------------------------------------------------------
# Legitimate messages
# ---------------------------------------------------------

def legitimate_message():
    templates = [
        (
            "Your UPI payment of ₹850 was successful. "
            "Transaction reference: 458921763214."
        ),
        (
            "Your SBI account statement for July 2026 is available. "
            "Please use the official SBI YONO app to view it."
        ),
        (
            "Your electricity bill for August 2026 is ready. "
            "Please view it through the official electricity provider website."
        ),
        (
            "Your Amazon order has been shipped and will be delivered soon. "
            "Track your package through the official Amazon app."
        ),
        (
            "Your Aadhaar update request has been successfully submitted. "
            "Check the status through the official UIDAI website."
        ),
        (
            "Your Flipkart order has been delivered successfully. "
            "Thank you for shopping with us."
        ),
        (
            "Your college examination timetable has been published. "
            "Please check the official student portal."
        ),
        (
            "Your bank payment was successfully completed. "
            "Transaction ID has been generated for your records."
        ),
    ]

    return random.choice(templates), None, "legitimate"


# ---------------------------------------------------------
# Generator selection
# ---------------------------------------------------------

SCAM_GENERATORS = [
    kyc_scam,
    upi_scam,
    prize_scam,
    electricity_scam,
    delivery_scam,
    loan_scam,
    telecom_scam,
    government_scam,
    hindi_scam,
    marathi_scam,
    hinglish_scam,
]

# ---------------------------------------------------------
# URL extraction
# ---------------------------------------------------------

URL_REGEX = re.compile(
    r"https?://[^\s<>\"]+",
    re.IGNORECASE,
)


def extract_urls(text):
    return URL_REGEX.findall(text)


# ---------------------------------------------------------
# Main generator
# ---------------------------------------------------------

def generate_case(index):
    # Keep approximately 40% legitimate and 60% scam.
    is_legitimate = index < int(TOTAL_ROWS * 0.40)

    if is_legitimate:
        text, url, category = legitimate_message()
        risk = "low"
    else:
        generator = random.choice(SCAM_GENERATORS)
        text, url, category = generator()
        risk = "high"

    urls = extract_urls(text)

    # If URL was explicitly generated but wasn't caught for any reason,
    # include it in the extracted URL field.
    if url and url not in urls:
        urls.append(url)

    return {
        "case_id": f"DD-QA-{index + 1:05d}",
        "raw_text": text,
        "expected_risk_level": risk,
        "extracted_urls": "|".join(urls),
        "scam_category": category,
        "region": random.choice(REGIONS),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = [generate_case(i) for i in range(TOTAL_ROWS)]

    fieldnames = [
        "case_id",
        "raw_text",
        "expected_risk_level",
        "extracted_urls",
        "scam_category",
        "region",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    scam_count = sum(
        row["expected_risk_level"] == "high"
        for row in rows
    )

    legitimate_count = TOTAL_ROWS - scam_count

    print("=" * 60)
    print("DhokaDetect QA Dataset Generator")
    print("=" * 60)
    print(f"Total cases      : {TOTAL_ROWS}")
    print(f"Scam cases       : {scam_count}")
    print(f"Legitimate cases : {legitimate_count}")
    print(f"Output           : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()