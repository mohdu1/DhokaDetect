import requests
import base64

# Change this to "real_payment.jpg" or "fake_payment.jpg"
IMAGE_PATH = "real_payment.jpeg" 
API_URL = "http://127.0.0.1:8001/detect-media"

print(f"Sending {IMAGE_PATH} to Vision Microservice...")

try:
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": (IMAGE_PATH, f, "image/jpeg")}
        response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Detection Complete!")
        print(f"File: {data['filename']}")
        print(f"Fraud Probability Score: {data['fraud_probability']}")
        
        # Decode the base64 heatmap back into a real image
        if data.get("heatmap_base64"):
            img_data = base64.b64decode(data['heatmap_base64'])
            heatmap_filename = f"heatmap_{IMAGE_PATH}"
            with open(heatmap_filename, "wb") as out_file:
                out_file.write(img_data)
            print(f"🔥 Heatmap saved as '{heatmap_filename}'. Open it to see the highlighted pixels!")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except FileNotFoundError:
    print(f"Error: Could not find {IMAGE_PATH}. Make sure the image is in the same folder.")