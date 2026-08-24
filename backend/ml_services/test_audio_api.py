import requests
import os
import mimetypes

API_URL = "http://localhost:8001/analyze-audio"
AUDIO_FILE = r"C:\Users\Manas Thaker\Downloads\i_just_wannamove.mp4"

def test_audio():
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Error: Could not find file at '{AUDIO_FILE}'. Check the file path.")
        return

    print(f"🎙️ Sending '{AUDIO_FILE}' to Audio Microservice...")

    mime_type, _ = mimetypes.guess_type(AUDIO_FILE)
    if not mime_type:
        mime_type = "video/mp4" if AUDIO_FILE.endswith(".mp4") else "audio/*"

    with open(AUDIO_FILE, "rb") as f:
        files = {"file": (os.path.basename(AUDIO_FILE), f, mime_type)}
        
        try:
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                print("\n✅ Analysis Complete!")
                data = response.json()
                
                print(f"File: {data.get('filename')}")
                print(f"Verdict: {data.get('verdict')}")
                print(f"Risk Score: {data.get('risk_score')}")
                print("Features:")
                
                for feature, value in data.get('features', {}).items():
                    print(f"  - {feature}: {value:.4f}")
            else:
                print(f"\n❌ Server Error ({response.status_code}): {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Connection Error: Is main3.py running on Port 8001?")

if __name__ == "__main__":
    test_audio()