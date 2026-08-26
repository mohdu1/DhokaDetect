from pathlib import Path
import shutil

MODEL_PATH = Path("backend/ml_services/model_manager.py")
BACKUP_PATH = Path("backend/ml_services/model_manager_before_english_fix.py")

# Safety backup
shutil.copy2(MODEL_PATH, BACKUP_PATH)

text = MODEL_PATH.read_text(encoding="utf-8-sig")

start = text.find("        self.strong_english_scam_patterns = [")
end = text.find("        self.strong_hindi_scam_patterns = [", start)

if start == -1:
    raise RuntimeError("Could not find strong_english_scam_patterns")

if end == -1:
    raise RuntimeError("Could not find strong_hindi_scam_patterns")

replacement = r'''        self.strong_english_scam_patterns = [
            # KYC expiry + sensitive identity documents + urgency
            (
                r"\bkyc\b.{0,80}(?:expired|incomplete|pending).{0,120}"
                r"(?:submit|provide|share).{0,80}"
                r"(?:pan|aadhaar).{0,100}"
                r"(?:within|today|immediately|urgent|\d+\s*hours?)"
            ),

            # KYC expiry + PAN/Aadhaar + urgency
            (
                r"\bkyc\b.{0,100}(?:expired|incomplete|pending).{0,160}"
                r"(?:pan|aadhaar).{0,120}"
                r"(?:within|today|immediately|urgent|\d+\s*hours?)"
            ),
        ]

'''

new_text = text[:start] + replacement + text[end:]

MODEL_PATH.write_text(new_text, encoding="utf-8")

print("English scam pattern repaired.")
print(f"Backup created: {BACKUP_PATH}")