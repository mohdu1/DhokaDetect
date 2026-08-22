import requests
import base64

IMAGE_PATH = r"C:\Users\Manas Thaker\OneDrive\Desktop\DhokaDetect\backend\ml_services\dataset\Fake\WhatsApp Image 2026-08-23 at 1.14.48 AM.jpeg"
API_URL = "http://127.0.0.1:8001/detect-media"

print(f"Sending {IMAGE_PATH} to Vision Microservice...")

try:
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": (IMAGE_PATH, f, "image/jpeg")}
        # Tell the server which model to use ("payment" or "deepfake")
        data = {"task": "payment"} 
        
        # Send both the file and the task data
        response = requests.post(API_URL, files=files, data=data)

    if response.status_code == 200:
        response_data = response.json()
        print(f"\n✅ Detection Complete!")
        print(f"File: {response_data['filename']}")
        print(f"Mode Used: {response_data.get('mode_used', 'N/A')}")
        print(f"Fraud Probability Score: {response_data['fraud_probability']}")
        
        # Decode the base64 heatmap back into a real image
        if response_data.get("heatmap_base64"):
            img_data = base64.b64decode(response_data['heatmap_base64'])
            heatmap_filename = f"heatmap_{IMAGE_PATH}"
            with open(heatmap_filename, "wb") as out_file:
                out_file.write(img_data)
            print(f"🔥 Heatmap saved as '{heatmap_filename}'. Open it to see the highlighted pixels!")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except FileNotFoundError:
    print(f"Error: Could not find '{IMAGE_PATH}'. Make sure the image is in the same folder as this script.")