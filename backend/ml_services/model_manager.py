import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import time

class LocalScamDetector:
    def __init__(self, model_name: str = "mariagrandury/distilbert-base-uncased-finetuned-sms-spam-detection"):
        print(f"Loading tokenizer and model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        # Local Rule-Engine Patterns for Indian Payment/Social Engineering Scams
        self.urgency_patterns = [
            r"within \d+ mins?", r"immediate(ly)?", r"today", r"avoid disconnection", r"account will be blocked"
        ]
        self.impersonation_patterns = [
            r"\bmseb\b", r"electricity board", r"\bsbi\b", r"\bhdfc\b", r"\bkyc\b", r"update pan", r"\bupi\b"
        ]
        self.suspicious_link_patterns = [
            r"bit\.ly", r"tinyurl\.com", r"http://", r"-\w+\.in", r"-\w+\.com"
        ]

    def _extract_heuristics(self, text: str):
        """Extracts red flags and calculates a local heuristic risk score."""
        red_flags = []
        score = 0.0
        text_lower = text.lower()

        if any(re.search(p, text_lower) for p in self.urgency_patterns):
            red_flags.append("Fake Urgency / Pressure Tactics Detected")
            score += 0.35

        if any(re.search(p, text_lower) for p in self.impersonation_patterns):
            red_flags.append("Entity / Utility Impersonation Pattern Detected")
            score += 0.30

        if any(re.search(p, text_lower) for p in self.suspicious_link_patterns):
            red_flags.append("Suspicious or Unofficial Link / Shortened URL Detected")
            score += 0.35

        return round(min(score, 1.0), 4), red_flags

    def predict(self, texts: list):
        inputs = self.tokenizer(
            texts, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=128
        ).to(self.device)

        with torch.no_grad():
            start_time = time.time()
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            inference_time = time.time() - start_time

        results = []
        for i, prob in enumerate(probabilities):
            text = texts[i]
            bert_scam_prob = prob[1].item()
            
            heuristic_score, red_flags = self._extract_heuristics(text)
            hybrid_scam_score = round(max(bert_scam_prob, heuristic_score if heuristic_score > 0 else bert_scam_prob), 4)
            
            results.append({
                "text": text,
                "prediction": "SCAM" if hybrid_scam_score > 0.5 else "LEGIT",
                "scam_confidence": hybrid_scam_score,
                "ml_bert_score": round(bert_scam_prob, 4),
                "heuristic_score": heuristic_score,
                "red_flags": red_flags
            })
            
        return results, inference_time