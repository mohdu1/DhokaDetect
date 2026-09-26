import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.ml_services.model_manager import LocalScamDetector

def main():
    print("=" * 70)
    print("DhokaDetect — Unseen Message Test")
    print("=" * 70)

    model = LocalScamDetector()

    test_messages = [
        # SCAM — Banking
        "URGENT: Your SBI account will be blocked today. Verify your KYC immediately at https://sbi-kyc-update.in",

        # SCAM — UPI
        "Your UPI ID has been suspended. Click https://upi-secure-verification.in to reactivate now.",

        # SCAM — Electricity
        "Your electricity connection will be disconnected tonight due to unpaid bill. Pay immediately at https://mahadiscom-bill.in",

        # SCAM — KYC
        "Your KYC has expired. Submit your PAN and Aadhaar details within 2 hours to avoid account suspension.",

        # SCAM — Prize
        "Congratulations! You have won ₹25,00,000 in the lucky draw. Pay ₹5,000 processing fee to claim your prize.",

        # HINDI SCAM
        "आपका बैंक खाता बंद होने वाला है। तुरंत KYC अपडेट करें और इस लिंक पर क्लिक करें।",

        # HINGLISH SCAM
        "Aapka SBI account block hone wala hai. Abhi KYC update karo warna account permanently band ho jayega.",

        # MARATHI SCAM
        "तुमचे बँक खाते बंद होणार आहे. कृपया त्वरित KYC अपडेट करा आणि लिंकवर क्लिक करा.",

        # LEGITIMATE
        "Your Aadhaar update request has been successfully submitted. Check the status through the official UIDAI website.",

        # LEGITIMATE
        "Your SBI transaction of Rs. 2,500 was successful. Thank you for banking with us.",

        # LEGITIMATE
        "Your electricity bill payment of Rs. 1,240 was received successfully. Thank you.",

        # LEGITIMATE
        "Your UPI payment of Rs. 500 to Rahul was successful.",

        # LEGITIMATE
        "Your PAN card has been dispatched. You can track the delivery using the official portal.",
    ]

    results, inference_time = model.predict(test_messages)

    print(f"\nInference time: {inference_time:.4f}s")
    print("\n" + "=" * 70)

    for i, result in enumerate(results, 1):
        print(f"\nTEST {i}")
        print("-" * 70)
        print("Message:")
        print(result["text"])

        print("\nPrediction:")
        print(result["prediction"])

        print("Scam confidence:")
        print(result["scam_confidence"])

        print("BERT score:")
        print(result["ml_bert_score"])

        print("Heuristic score:")
        print(result["heuristic_score"])

        print("Red flags:")
        print(result["red_flags"])

    print("\n" + "=" * 70)
    print("Testing complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()