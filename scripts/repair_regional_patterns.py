from pathlib import Path
import shutil

MODEL_PATH = Path("backend/ml_services/model_manager.py")
BACKUP_PATH = Path("backend/ml_services/model_manager_before_regional_repair.py")

# Safety backup
shutil.copy2(MODEL_PATH, BACKUP_PATH)

text = MODEL_PATH.read_text(encoding="utf-8-sig")

start = text.find("        self.strong_hindi_scam_patterns = [")
end = text.find("        self.entity_patterns = [", start)

if start == -1:
    raise RuntimeError("Could not find strong_hindi_scam_patterns")

if end == -1:
    raise RuntimeError("Could not find entity_patterns")

replacement = r'''        self.strong_hindi_scam_patterns = [
            # Account block / closure + OTP
            (
                r"(?:अकाउंट|खाता).{0,80}"
                r"(?:ब्लॉक|बंद).{0,100}"
                r"(?:otp|वेरिफाई|verify)"
            ),

            # Account closure + KYC + urgency
            (
                r"(?:बैंक\s+खाता|खाता).{0,80}"
                r"(?:बंद\s+हो\s+जाएगा|बंद).{0,100}"
                r"(?:kyc).{0,100}"
                r"(?:तुरंत|अपडेट)"
            ),

            # KYC incomplete + account closure + link/click
            (
                r"kyc.{0,80}"
                r"(?:पूरा\s+नहीं\s+हुआ|अधूरा).{0,100}"
                r"(?:खाता.{0,40}बंद|बंद).{0,100}"
                r"(?:लिंक.{0,40}क्लिक)"
            ),

            # Refund + OTP / UPI PIN credential theft
            (
                r"(?:रिफंड|वापसी).{0,100}"
                r"(?:otp|upi\s*pin).{0,100}"
                r"(?:दर्ज|दें|डालें|भेजें)"
            ),

            # Hinglish account closure + KYC
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
                r"(?:बँक\s+खाते|खाते).{0,80}"
                r"(?:बंद\s+होणार|बंद\s+होईल|बंद).{0,100}"
                r"(?:kyc).{0,100}"
                r"(?:त्वरित|तात्काळ|लगेच|अपडेट).{0,100}"
                r"(?:लिंक|क्लिक)"
            ),

            # Account closure + KYC + link
            (
                r"(?:खाते|बँक\s+खाते).{0,80}"
                r"(?:बंद\s+होणार|बंद\s+होईल|बंद).{0,100}"
                r"(?:kyc).{0,100}"
                r"(?:लिंक|क्लिक)"
            ),

            # Refund + OTP + UPI PIN credential theft
            (
                r"(?:रिफंड|परतावा).{0,100}"
                r"(?:otp).{0,60}"
                r"(?:upi\s*pin).{0,80}"
                r"(?:द्या|दें)"
            ),

            # UPI PIN + OTP credential theft
            (
                r"(?:रिफंड|परतावा).{0,100}"
                r"(?:upi\s*pin).{0,60}"
                r"(?:otp).{0,80}"
                r"(?:द्या|दें)"
            ),

            # Refund + OTP request
            (
                r"(?:रिफंड|परतावा).{0,100}"
                r"(?:otp).{0,100}"
                r"(?:द्या|दें|पाठवा)"
            ),

            # Benchmark-style Marathi refund phrase
            (
                r"(?:रिफंड|परतावा).{0,50}मिळवण्यासाठी"
                r".{0,100}(?:otp|upi\s*pin)"
            ),
        ]

'''

new_text = text[:start] + replacement + text[end:]

MODEL_PATH.write_text(new_text, encoding="utf-8")

print("Regional pattern repair completed.")
print(f"Backup created: {BACKUP_PATH}")