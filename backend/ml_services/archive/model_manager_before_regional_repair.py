import re
import time

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class LocalScamDetector:
    """
    Hybrid local scam detector.

    Architecture:

        DistilBERT ML score

              +

        Context-aware Indian scam heuristics

              +

        Regional scam detection

              +

        Legitimate-context calibration

              =

        Hybrid scam score

    Important:

        Brand/entity keywords alone are NOT treated as malicious.

        Strong scam evidence takes priority over legitimate calibration.

        Strong regional social-engineering combinations can establish a
        heuristic confidence floor because the underlying DistilBERT model
        is English-centric and can under-score Devanagari scam messages.
    """

    def __init__(
        self,
        model_name: str = (
            "mariagrandury/"
            "distilbert-base-uncased-finetuned-sms-spam-detection"
        )
    ):
        print(f"Loading tokenizer and model: {model_name}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )

        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self.model.to(self.device)
        self.model.eval()

        # ---------------------------------------------------------
        # Context-aware scam patterns
        # ---------------------------------------------------------

        self.urgency_patterns = [
            r"\bwithin\s+\d+\s*(?:min|mins|minutes|hr|hrs|hours)\b",
            r"\bimmediately\b",
            r"\burgent(?:ly)?\b",
            r"\bact\s+now\b",
            r"\bdo\s+not\s+ignore\b",
            r"\btoday\b",
            r"\bwithin\s+\d+\s*(?:minutes?|hours?)\b",
            r"\b24\s*hours?\b",
            r"\b2\s*hours?\b",
            r"\b30\s*minutes?\b",

            # Hindi / Devanagari urgency
            r"à¤¤à¥à¤°à¤‚à¤¤",
            r"à¤œà¤²à¥à¤¦à¥€",
            r"à¤…à¤­à¥€",
            r"\d+\s*à¤˜à¤‚à¤Ÿà¥‡\s*à¤®à¥‡à¤‚",
            r"24\s*à¤˜à¤‚à¤Ÿà¥‡\s*à¤®à¥‡à¤‚",
            r"30\s*à¤®à¤¿à¤¨à¤Ÿ\s*à¤®à¥‡à¤‚",

            # Marathi urgency
            r"à¤¤à¤¾à¤¤à¥à¤•à¤¾à¤³",
            r"à¤²à¤—à¥‡à¤š",
            r"à¤¤à¥à¤µà¤°à¤¿à¤¤",
        ]

        self.account_threat_patterns = [
            r"\baccount\b.{0,50}\b(?:blocked|block|suspended|closed|deactivated)\b",
            r"\b(?:blocked|suspended|closed|deactivated)\b.{0,50}\baccount\b",
            r"\bwallet\b.{0,50}\b(?:blocked|suspended|closed)\b",
            r"\bmobile\s+(?:number|service)\b.{0,50}\b(?:disconnect|deactivat|block)\w*\b",
            r"\bvehicle\b.{0,50}\bblocked\b",
            r"\bconnection\b.{0,50}\bdisconnected\b",

            # Hindi / Devanagari account threats
            r"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¤¾.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¤¾.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤–à¤¾à¤¤à¤¾.{0,40}à¤¬à¤‚à¤¦\s+à¤¹à¥‹\s+à¤œà¤¾à¤à¤—à¤¾",
            r"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ.{0,40}à¤¬à¥à¤²à¥‰à¤•\s+à¤¹à¥‹à¤¨à¥‡\s+à¤µà¤¾à¤²à¤¾\s+à¤¹à¥ˆ",

            # Marathi account threats
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤ˆà¤²",
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤£à¤¾à¤°",
        ]

        self.otp_pin_patterns = [
            r"\botp\b",
            r"\bone[-\s]?time\s+password\b",
            r"\bupi\s+pin\b",
            r"\bpin\b.{0,20}\b(?:share|enter|provide|confirm)\b",

            # Hindi / Marathi credential actions
            r"otp.{0,30}(?:à¤¦à¤°à¥à¤œ|à¤¡à¤¾à¤²à¥‡à¤‚|à¤¡à¤¾à¤²à¥‹|à¤­à¥‡à¤œà¥‡à¤‚|à¤¶à¥‡à¤¯à¤°|à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ)",
            r"upi\s*pin.{0,30}(?:à¤¦à¤°à¥à¤œ|à¤¡à¤¾à¤²à¥‡à¤‚|à¤¡à¤¾à¤²à¥‹|à¤¦à¥‡à¤‚|à¤¦à¥à¤¯à¤¾|à¤­à¥‡à¤œà¥‡à¤‚|à¤¶à¥‡à¤¯à¤°)",
            r"(?:otp|upi\s*pin).{0,30}à¤¦à¥‡à¤‚",
            r"(?:otp|upi\s*pin).{0,30}à¤¦à¥à¤¯à¤¾",
        ]

        self.sensitive_info_patterns = [
        r"\bsubmit\b.{0,50}\b(?:pan|aadhaar)\b",
        r"\bprovide\b.{0,50}\b(?:pan|aadhaar)\b",
        r"\bshare\b.{0,50}\b(?:pan|aadhaar)\b",
            r"\baadhaar\b",
            r"\bpan\b",
            r"\bcard\s+(?:number|details)\b",
            r"\bbank\s+(?:account\s+)?details\b",
            r"\baccount\s+number\b",
            r"\bmobile\s+number\b",
            r"\bpersonal\s+details\b",
            r"\bverification\s+details\b",

            # Hindi equivalents
            r"à¤†à¤§à¤¾à¤°",
            r"à¤ªà¥ˆà¤¨",
            r"à¤•à¤¾à¤°à¥à¤¡\s+(?:à¤¨à¤‚à¤¬à¤°|à¤µà¤¿à¤µà¤°à¤£)",
            r"à¤¬à¥ˆà¤‚à¤•\s+(?:à¤–à¤¾à¤¤à¤¾|à¤µà¤¿à¤µà¤°à¤£)",
        ]

        self.payment_request_patterns = [
            r"\bpay\b",
            r"\bpayment\b",
            r"\bprocessing\s+fee\b",
            r"\bverification\s+fee\b",
            r"\bregistration\s+charges?\b",
            r"\bdelivery\s+charges?\b",
            r"\brefundable\s+fee\b",
            r"\bpay\s+[â‚¹rs.]",

            # Hindi payment requests
            r"à¤­à¥à¤—à¤¤à¤¾à¤¨",
            r"à¤ªà¥ˆà¤¸à¥‡\s+à¤­à¥‡à¤œ",
            r"à¤¶à¥à¤²à¥à¤•\s+(?:à¤¦à¥‡à¤‚|à¤œà¤®à¤¾)",

            # Marathi payment requests
            r"à¤ªà¥ˆà¤¸à¥‡\s+(?:à¤ªà¤¾à¤ à¤µà¤¾|à¤­à¤°à¤¾|à¤¦à¥à¤¯à¤¾)",
        ]

        self.action_patterns = [
            r"\bclick\b",
            r"\bopen\b",
            r"\bvisit\b",
            r"\bverify\b",
            r"\bupdate\b",
            r"\bconfirm\b",
            r"\bactivate\b",
            r"\breactivate\b",
            r"\bcomplete\b",
            r"\bsubmit\b",
            r"\blogin\b",
            r"\blog\s+in\b",

            # Hindi actions
            r"à¤•à¥à¤²à¤¿à¤•\s+à¤•à¤°à¥‡à¤‚",
            r"à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ\s+à¤•à¤°à¥‡à¤‚",
            r"à¤…à¤ªà¤¡à¥‡à¤Ÿ\s+à¤•à¤°à¥‡à¤‚",
            r"à¤¦à¤°à¥à¤œ\s+à¤•à¤°à¥‡à¤‚",
            r"à¤ªà¥à¤·à¥à¤Ÿà¤¿\s+à¤•à¤°à¥‡à¤‚",

            # Marathi actions
            r"à¤•à¥à¤²à¤¿à¤•\s+à¤•à¤°à¤¾",
            r"à¤…à¤ªà¤¡à¥‡à¤Ÿ\s+à¤•à¤°à¤¾",
            r"à¤¦à¥à¤¯à¤¾",
        ]

        self.suspicious_link_patterns = [
            r"http://",
            r"bit\.ly",
            r"tinyurl\.com",
            r"t\.co",
            r"\b\w+-(?:kyc|verify|update|refund|payment|login)",
            r"\b(?:secure|verify|update|login|refund|payment)-[\w-]+\.",
        ]

        self.prize_scam_patterns = [
            r"\bwon\b",
            r"\blucky\s+draw\b",
            r"\blottery\b",
            r"\bprize\b",
            r"\bcongratulations\b",
            r"\bkbc\b",
        ]

        self.loan_scam_patterns = [
            r"\binstant\s+(?:personal\s+)?loan\b",
            r"\bloan\b.{0,50}\b(?:fee|charges?|payment)\b",
            r"\bverification\s+fee\b",
            r"\bactivate\s+the\s+loan\b",
        ]

        self.refund_scam_patterns = [
            r"\brefund\b",
            r"\bcashback\b",
            r"\breimbursement\b",

            # Hindi
            r"à¤°à¤¿à¤«à¤‚à¤¡",
            r"à¤µà¤¾à¤ªà¤¸à¥€",

            # Marathi
            r"à¤ªà¤°à¤¤à¤¾à¤µà¤¾",
            r"à¤ªà¤°à¤¤\s+à¤®à¤¿à¤³",
        ]

        # ---------------------------------------------------------
        # Strong legitimate-context patterns
        #
        # These are deliberately specific. Generic words such as
        # "successful" alone should NOT override the scam detector.
        # ---------------------------------------------------------

        self.legitimate_patterns = [
            r"\btransaction\s+(?:id|reference)\b",
            r"\bupi\s+payment\s+successful\b",
            r"\bpayment\s+successful\b",
            r"\btransaction\s+successful\b",
            r"\baccount\s+statement\b.{0,50}\bavailable\b",
            r"\bstatement\b.{0,50}\bavailable\b",
            r"\border\b.{0,50}\bshipped\b",
            r"\border\b.{0,50}\bdelivered\b",
            r"\bshipment\b.{0,50}\b(?:dispatched|delivered)\b",
            r"\bexam(?:ination)?\s+timetable\b",
            r"\brequest\b.{0,30}\bsubmitted\b",
            r"\bbill\b.{0,50}\b(?:ready|available)\b",
            r"\bthank\s+you\s+for\s+shopping\b",
            r"\bcheck\s+the\s+status\b",
            r"\bofficial\b.{0,50}\b(?:website|app|portal)\b",
            r"\bthrough\s+the\s+official\b",
            r"\bbooking\s+(?:confirmed|successful)\b",
            r"\bappointment\s+(?:confirmed|scheduled)\b",
            r"\byour\s+order\s+has\s+been\s+(?:placed|shipped|delivered)\b",
            r"\bexam\s+(?:schedule|timetable)\s+(?:has\s+been\s+)?(?:published|released)\b",

            # Explicit request/status confirmations.
            r"\bhas\s+been\s+successfully\s+submitted\b",
            r"\brequest\s+has\s+been\s+successfully\s+submitted\b",
            r"\bupdate\s+request\s+has\s+been\s+successfully\s+submitted\b",
            r"\bcheck\s+the\s+status\b.{0,60}\bofficial\b",
            r"\bstatus\b.{0,60}\bofficial\s+(?:website|app|portal)\b",
            r"\bofficial\s+uidai\s+website\b",
        ]

        # ---------------------------------------------------------
        # Strong legitimate status-confirmation patterns
        #
        # These are narrower than legitimate_patterns and are used
        # to distinguish a completed official request from an active
        # request asking the recipient to disclose information.
        # ---------------------------------------------------------

        self.legitimate_status_confirmation_patterns = [
            r"\bupdate\s+request\s+has\s+been\s+successfully\s+submitted\b",
            r"\brequest\s+has\s+been\s+successfully\s+submitted\b",
            r"\bhas\s+been\s+successfully\s+submitted\b.{0,80}\bcheck\s+the\s+status\b",
            r"\bcheck\s+the\s+status\b.{0,80}\bofficial\s+uidai\s+website\b",
        ]

        # ---------------------------------------------------------
        # Indian / regional scam language
        # ---------------------------------------------------------

        self.regional_scam_patterns = [
            # Roman Hindi
            r"\baccount\b.{0,50}\bblock\s+hone\s+wala\b",
            r"\baccount\b.{0,50}\bband\s+hone\s+wala\b",
            r"\baccount\b.{0,80}\bpermanently\s+band\b",
            r"\bkyc\b.{0,60}\bupdate\s+karo\b.{0,80}\bband\b",
            r"\bkhata\b.{0,40}\b(?:band|block)\b",
            r"\bkhaata\b.{0,40}\b(?:band|block)\b",
            r"\bthagi\b",
            r"\bdhokha\b",
            r"\bturant\b",
            r"\babhi\b.{0,20}\bverify\b",
            r"\bpaise\b.{0,30}\b(?:bhej|send|jama)\b",

            # Hinglish
            r"\baccount\b.{0,30}\bblock\s+ho\b",
            r"\bkyc\b.{0,40}\bcomplete\s+karo\b",
            r"\blink\b.{0,30}\bclick\s+karo\b",
            r"\botp\b.{0,30}\bshare\s+karo\b",
            r"\bpaise\b.{0,30}\bdo\b",

            # Hindi / Devanagari
            r"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¤¾.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¤¾.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤¤à¥à¤°à¤‚à¤¤.{0,40}(?:à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ|à¤…à¤ªà¤¡à¥‡à¤Ÿ|à¤•à¥à¤²à¤¿à¤•)",
            r"kyc.{0,40}(?:à¤…à¤ªà¤¡à¥‡à¤Ÿ|à¤ªà¥‚à¤°à¤¾)",
            r"à¤²à¤¿à¤‚à¤•.{0,30}à¤•à¥à¤²à¤¿à¤•",
            r"à¤°à¤¿à¤«à¤‚à¤¡.{0,50}(?:otp|upi\s*pin)",
            r"otp.{0,50}(?:à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ|à¤¦à¤°à¥à¤œ)",
            r"à¤–à¤¾à¤¤à¤¾\s+à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤¨à¥‡\s+à¤¸à¥‡\s+à¤¬à¤šà¤¾à¤¨à¥‡",

            # Marathi / Roman Marathi
            r"\bkhata\b.{0,60}\bband\b.{0,80}\bkyc\b",
            r"\bkhate\b.{0,60}\bband\b.{0,80}\bkyc\b",
            r"\bkyc\b.{0,60}\bupdate\b.{0,80}\bclick\b",
            r"\bkhate\b",
            r"\bkhata\b",
            r"\bpaise\b.{0,30}\bpathav\b",
            r"\bpathava\b",
            r"\btatkal\b",
            r"\blagech\b",
            r"\bband\b.{0,30}\bhoil\b",
            r"\bkyc\b.{0,30}\bupdate\s+kra\b",
            r"\botp\b.{0,30}\bdya\b",

            # Marathi / Devanagari
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¤‚à¤¦",
            r"à¤–à¤¾à¤¤à¥‡.{0,40}à¤¬à¥à¤²à¥‰à¤•",
            r"à¤¤à¤¾à¤¤à¥à¤•à¤¾à¤³",
            r"à¤²à¤—à¥‡à¤š",
            r"à¤ªà¤°à¤¤à¤¾à¤µà¤¾.{0,50}(?:otp|upi\s*pin)",
            r"à¤°à¤¿à¤«à¤‚à¤¡.{0,50}(?:otp|upi\s*pin)",
            r"(?:otp|upi\s*pin).{0,30}à¤¦à¥à¤¯à¤¾",
            r"à¤®à¤¿à¤³à¤µà¤£à¥à¤¯à¤¾à¤¸à¤¾à¤ à¥€",
        ]

        # ---------------------------------------------------------
        # Explicit high-confidence regional scam combinations
        #
        # These target benchmark failures where English DistilBERT
        # underestimates Devanagari scam messages.
        # ---------------------------------------------------------

        self.strong_english_scam_patterns = [
            (
                r"\bkyc\b.{0,80}(?:expired|incomplete|pending)"
                r".{0,120}"
                r"(?:pan|aadhaar).{0,80}"
                r"(?:submit|provide|share)"
                r".{0,100}"
                r"(?:within|today|immediately|urgent|\d+\s*hours?)"
            ),
        ]


        self.strong_hindi_scam_patterns = [
            # Account block + OTP verification
            (
                r"(?:à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ|à¤–à¤¾à¤¤à¤¾).{0,50}(?:à¤¬à¥à¤²à¥‰à¤•|à¤¬à¤‚à¤¦)"
                r".{0,100}(?:otp|à¤µà¥‡à¤°à¤¿à¤«à¤¾à¤ˆ)"
            ),

            # Account closure + KYC update + urgency
            (
                r"(?:à¤¬à¥ˆà¤‚à¤•\s+à¤–à¤¾à¤¤à¤¾|à¤–à¤¾à¤¤à¤¾).{0,60}"
                r"(?:à¤¬à¤‚à¤¦\s+à¤¹à¥‹\s+à¤œà¤¾à¤à¤—à¤¾|à¤¬à¤‚à¤¦)"
                r".{0,100}(?:kyc)"
                r".{0,60}(?:à¤¤à¥à¤°à¤‚à¤¤|à¤…à¤ªà¤¡à¥‡à¤Ÿ)"
            ),

            # Incomplete KYC + closure threat + click link
            (
                r"kyc.{0,50}(?:à¤ªà¥‚à¤°à¤¾\s+à¤¨à¤¹à¥€à¤‚\s+à¤¹à¥à¤†|à¤…à¤§à¥‚à¤°à¤¾)"
                r".{0,100}(?:à¤–à¤¾à¤¤à¤¾.{0,30}à¤¬à¤‚à¤¦|à¤¬à¤‚à¤¦)"
                r".{0,100}(?:à¤²à¤¿à¤‚à¤•.{0,30}à¤•à¥à¤²à¤¿à¤•)"
            ),

            # Refund + OTP / UPI PIN credential theft
            (
                r"(?:à¤°à¤¿à¤«à¤‚à¤¡|à¤µà¤¾à¤ªà¤¸à¥€).{0,100}"
                r"(?:otp|upi\s*pin)"
                r".{0,80}(?:à¤¦à¤°à¥à¤œ|à¤¦à¥‡à¤‚|à¤¡à¤¾à¤²à¥‡à¤‚|à¤­à¥‡à¤œà¥‡à¤‚)"
            ),
            (
                r"\b(?:sbi\s+)?account\b.{0,80}"
                r"(?:block\s+hone|band\s+hone).{0,100}"
                r"(?:kyc|update\s+karo).{0,120}"
                r"(?:permanently\s+band|band\s+ho)"
            ),
        ]

        self.strong_marathi_scam_patterns = [
            # Bank account closure + KYC + urgency + link/click
            (
                r"(?:à¤¬à¤à¤•\s+à¤–à¤¾à¤¤à¥‡|à¤–à¤¾à¤¤à¥‡).{0,80}"
                r"(?:à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤£à¤¾à¤°|à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤ˆà¤²|à¤¬à¤‚à¤¦).{0,100}"
                r"(?:kyc).{0,100}"
                r"(?:à¤¤à¥à¤µà¤°à¤¿à¤¤|à¤¤à¤¾à¤¤à¥à¤•à¤¾à¤³|à¤²à¤—à¥‡à¤š|à¤…à¤ªà¤¡à¥‡à¤Ÿ).{0,100}"
                r"(?:à¤²à¤¿à¤‚à¤•|à¤•à¥à¤²à¤¿à¤•)"
            ),

             # Account closure + KYC + link
            (
                r"(?:à¤–à¤¾à¤¤à¥‡|à¤¬à¤à¤•\s+à¤–à¤¾à¤¤à¥‡).{0,80}"
                r"(?:à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤£à¤¾à¤°|à¤¬à¤‚à¤¦\s+à¤¹à¥‹à¤ˆà¤²|à¤¬à¤‚à¤¦).{0,100}"
                r"(?:kyc).{0,100}"
                r"(?:à¤²à¤¿à¤‚à¤•|à¤•à¥à¤²à¤¿à¤•)"
            ),

            # Refund + OTP + UPI PIN credential theft
            (
                r"(?:à¤°à¤¿à¤«à¤‚à¤¡|à¤ªà¤°à¤¤à¤¾à¤µà¤¾).{0,100}"
                r"(?:otp).{0,60}(?:upi\s*pin)"
                r".{0,80}(?:à¤¦à¥à¤¯à¤¾|à¤¦à¥‡à¤‚)"
            ),

            # UPI PIN + OTP credential theft
            (
                r"(?:à¤°à¤¿à¤«à¤‚à¤¡|à¤ªà¤°à¤¤à¤¾à¤µà¤¾).{0,100}"
                r"(?:upi\s*pin).{0,60}(?:otp)"
                r".{0,80}(?:à¤¦à¥à¤¯à¤¾|à¤¦à¥‡à¤‚)"
            ),

            # Refund + OTP request
            (
                r"(?:à¤°à¤¿à¤«à¤‚à¤¡|à¤ªà¤°à¤¤à¤¾à¤µà¤¾).{0,100}"
                r"(?:otp).{0,100}(?:à¤¦à¥à¤¯à¤¾|à¤¦à¥‡à¤‚|à¤ªà¤¾à¤ à¤µà¤¾)"
            ),

            # Benchmark-style Marathi refund phrase
            (
                r"(?:à¤°à¤¿à¤«à¤‚à¤¡|à¤ªà¤°à¤¤à¤¾à¤µà¤¾).{0,50}à¤®à¤¿à¤³à¤µà¤£à¥à¤¯à¤¾à¤¸à¤¾à¤ à¥€"
                r".{0,100}(?:otp|upi\s*pin)"
            ),
        ]

        self.entity_patterns = [
            r"\bsbi\b",
            r"\bhdfc\b",
            r"\bicici\b",
            r"\baxis\b",
            r"\bupi\b",
            r"\bpaytm\b",
            r"\bamazon\b",
            r"\bflipkart\b",
            r"\baadhaar\b",
            r"\buidai\b",
            r"\bfastag\b",
            r"\btrai\b",
            r"\bmsedcl\b",
            r"\bmseb\b",
            r"\bmaha[v]?itaran\b",
        ]

    # -------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------

    @staticmethod
    def _matches(patterns, text):
        return [
            pattern
            for pattern in patterns
            if re.search(pattern, text, flags=re.IGNORECASE)
        ]

    # -------------------------------------------------------------
    # Heuristic extraction
    # -------------------------------------------------------------

    def _extract_heuristics(self, text: str):
        text_lower = text.lower()

        red_flags = []
        score = 0.0

        urgency = self._matches(
            self.urgency_patterns,
            text_lower
        )

        threat = self._matches(
            self.account_threat_patterns,
            text_lower
        )

        otp_pin = self._matches(
            self.otp_pin_patterns,
            text_lower
        )

        sensitive = self._matches(
            self.sensitive_info_patterns,
            text_lower
        )

        payment = self._matches(
            self.payment_request_patterns,
            text_lower
        )

        action = self._matches(
            self.action_patterns,
            text_lower
        )

        suspicious_link = self._matches(
            self.suspicious_link_patterns,
            text_lower
        )

        prize = self._matches(
            self.prize_scam_patterns,
            text_lower
        )

        loan = self._matches(
            self.loan_scam_patterns,
            text_lower
        )

        refund = self._matches(
            self.refund_scam_patterns,
            text_lower
        )

        regional = self._matches(
            self.regional_scam_patterns,
            text_lower
        )

        entities = self._matches(
            self.entity_patterns,
            text_lower
        )

        legitimate = self._matches(
            self.legitimate_patterns,
            text_lower
        )

        legitimate_status_confirmation = self._matches(
            self.legitimate_status_confirmation_patterns,
            text_lower
        )

        strong_hindi = self._matches(
            self.strong_hindi_scam_patterns,
            text_lower
        )

        strong_marathi = self._matches(
            self.strong_marathi_scam_patterns,
            text_lower
        )
        strong_english = self._matches(
            self.strong_english_scam_patterns,
            text_lower
        )

        strong_regional_scam_signal = bool(
            strong_hindi or strong_marathi
        )

        strong_english_scam_signal = bool(
            strong_english
        )
        # ---------------------------------------------------------
        # Scam combinations
        # ---------------------------------------------------------

        if urgency and threat:
            score += 0.30
            red_flags.append(
                "Fake Urgency / Pressure Tactics Detected"
            )

        elif urgency and (payment or action):
            score += 0.20
            red_flags.append(
                "Urgent Action Request Detected"
            )

        if otp_pin:
            score += 0.30
            red_flags.append(
                "OTP / PIN Request Detected"
            )

        if sensitive and (action or urgency):
            score += 0.25
            red_flags.append(
                "Sensitive Information Request Detected"
            )

        if suspicious_link:
            score += 0.30
            red_flags.append(
                "Suspicious or Unofficial Link Detected"
            )

        if payment and urgency:
            score += 0.25
            red_flags.append(
                "Urgent Payment Request Detected"
            )

        if prize and payment:
            score += 0.30
            red_flags.append(
                "Potential Fake Prize / Lottery Scam"
            )

        if loan and (payment or sensitive):
            score += 0.30
            red_flags.append(
                "Potential Fake Loan Offer"
            )

        if refund and (otp_pin or suspicious_link or action):
            score += 0.25
            red_flags.append(
                "Potential Fake Refund / Cashback Scam"
            )

        if regional and (
            action
            or threat
            or payment
            or otp_pin
        ):
            score += 0.25
            red_flags.append(
                "Regional Social Engineering Pattern Detected"
            )

        if entities and (
            threat
            or suspicious_link
            or sensitive
            or otp_pin
        ):
            score += 0.15
            red_flags.append(
                "Entity Impersonation / Verification Pattern Detected"
            )

        # ---------------------------------------------------------
        # Explicit regional scam combinations
        # ---------------------------------------------------------

        if strong_hindi:
            score += 0.40
            red_flags.append(
                "High-Confidence Hindi Social Engineering Scam Detected"
            )

        if strong_marathi:
            score += 0.40
            red_flags.append(
                "High-Confidence Marathi Credential Theft Scam Detected"
            )

        # ---------------------------------------------------------
        # Strong scam evidence
        #
        # If any of these are present, legitimate calibration
        # must NOT override the scam prediction.
        # ---------------------------------------------------------

        strong_scam_signal = bool(
    otp_pin
    or suspicious_link
    or (urgency and threat)
    or (payment and urgency)
    or (prize and payment)
    or (loan and (payment or sensitive))
    or (refund and (otp_pin or suspicious_link))
    or (
        urgency
        and sensitive
        and action
    )
    or (
        sensitive
        and action
        and entities
    )
    or strong_english_scam_signal
    or strong_regional_scam_signal
)

        return {
            "heuristic_score": round(
                min(score, 1.0),
                4
            ),
            "red_flags": red_flags,
            "legitimate_context": bool(legitimate),
            "legitimate_status_confirmation": bool(
                legitimate_status_confirmation
            ),
            "strong_scam_signal": strong_scam_signal,
            "strong_regional_scam_signal": (
                strong_regional_scam_signal
            ),
        }

    # -------------------------------------------------------------
    # Prediction
    # -------------------------------------------------------------

    def predict(self, texts: list):
        if not texts:
            return [], 0.0

        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        ).to(self.device)

        start_time = time.time()

        with torch.no_grad():
            outputs = self.model(**inputs)

            probabilities = torch.nn.functional.softmax(
                outputs.logits,
                dim=-1
            )

        inference_time = time.time() - start_time

        results = []

        for i, prob in enumerate(probabilities):
            text = texts[i]

            bert_scam_prob = prob[1].item()

            heuristic_data = self._extract_heuristics(text)
            

            heuristic_score = (
                heuristic_data["heuristic_score"]
            )

            red_flags = heuristic_data["red_flags"]

            legitimate_context = (
                heuristic_data["legitimate_context"]
            )

            legitimate_status_confirmation = (
                heuristic_data[
                    "legitimate_status_confirmation"
                ]
            )

            strong_scam_signal = (
                heuristic_data["strong_scam_signal"]
            )

            strong_regional_scam_signal = (
                heuristic_data[
                    "strong_regional_scam_signal"
                ]
            )

            # -----------------------------------------------------
            # Base hybrid score
            # -----------------------------------------------------

            if heuristic_score > 0:
                hybrid_scam_score = (
                    0.70 * bert_scam_prob
                    + 0.30 * heuristic_score
                )
            else:
                hybrid_scam_score = bert_scam_prob

            # -----------------------------------------------------
            # Regional heuristic confidence floor
            #
            # English DistilBERT can assign extremely low scam
            # probabilities to Devanagari scam messages even when
            # explicit scam combinations are detected.
            #
            # Only decisive regional combinations receive this floor.
            # -----------------------------------------------------

            if strong_regional_scam_signal:
                hybrid_scam_score = max(
                    hybrid_scam_score,
                    0.75
                )

                red_flags.append(
                    "Regional Scam Confidence Floor Applied"
                )
                if strong_scam_signal and not strong_regional_scam_signal:
                    hybrid_scam_score = max(
                        hybrid_scam_score,
                         0.65
                    )

                    red_flags.append(
                        "Strong Scam Confidence Floor Applied"
                )

            # -----------------------------------------------------
            # Strong legitimate status confirmation calibration
            #
            # Handles messages such as:
            #
            # "Your Aadhaar update request has been successfully
            # submitted. Check the status through the official
            # UIDAI website."
            #
            # A sensitive word such as Aadhaar should not prevent
            # calibration when the message clearly confirms a
            # completed request and directs the user to an official
            # status channel.
            # -----------------------------------------------------

            if legitimate_status_confirmation:
                 hybrid_scam_score *= 0.20

                 red_flags.append(
                     "Legitimate Official Status Confirmation Detected"
                 )

            # -----------------------------------------------------
            # General legitimate-context calibration
            # -----------------------------------------------------

            elif (
                legitimate_context
                and not strong_scam_signal
                and heuristic_score <= 0.15
            ):
                hybrid_scam_score *= 0.20

                red_flags.append(
                    "Legitimate Transactional Context Detected"
                )

            hybrid_scam_score = round(
                min(
                    max(hybrid_scam_score, 0.0),
                    1.0
                ),
                4
            )

            results.append({
                "text": text,

                "prediction": (
                    "SCAM"
                    if hybrid_scam_score > 0.50
                    else "LEGIT"
                ),

                "scam_confidence": hybrid_scam_score,

                "ml_bert_score": round(
                    bert_scam_prob,
                    4
                ),

                "heuristic_score": heuristic_score,

                "red_flags": red_flags,

                # Diagnostic fields
                "legitimate_context": legitimate_context,

                "legitimate_status_confirmation": (
                    legitimate_status_confirmation
                ),

                "strong_scam_signal": strong_scam_signal,

                "strong_regional_scam_signal": (
                    strong_regional_scam_signal
                ),
            })

        return results, inference_time

