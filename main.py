from PIL import Image, ImageDraw, ImageFont
import requests
import json
from datetime import datetime
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIGURATION ===
API_URL = "https://keyvalue.hamropatro.com/kv/get/market_segment_gold::1690855810198"
TEMPLATE_IMAGE = "template.png"
FONT_PATH = "arial.ttf"
FILENAME = "gold-price.png"
SERVICE_ACCOUNT_FILE = "service_account.json"
DRIVE_FOLDER_ID = "1nD5OEXFN2S7QCucpF8xArTjY4aYN-bJO"

GOLD_COORD = (680, 980)
SILVER_COORD = (680, 1300)
FONT_SIZE = 75
TEXT_COLOR_GOLD = "#F5A623"
TEXT_COLOR_SILVER = "#B0B0B0"

# === FETCH GOLD & SILVER PRICE ===
try:
    response = requests.get(API_URL)
    outer_json = response.json()
    value_str = outer_json["list"][0]["value"]
    data = json.loads(value_str)

    gold_price = silver_price = None

    for item in data["items"]:
        if item["name"] == "HalMark Gold":
            for p in item["prices"]:
                if p["name"] == "1 tola":
                    gold_price = p["price"]["price"]
        if item["name"] == "Silver":
            for p in item["prices"]:
                if p["name"] == "1 tola":
                    silver_price = p["price"]["price"]

    if not gold_price or not silver_price:
        raise ValueError("Missing gold or silver price")

except Exception as e:
    print(f"[ERROR] Price fetch failed: {e}")
    gold_price = "N/A"
    silver_price = "N/A"

# === GENERATE IMAGE ===
try:
    img = Image.open(TEMPLATE_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    draw.text(GOLD_COORD, f"Nrs {int(gold_price)} / TOLA", fill=TEXT_COLOR_GOLD, font=font)
    draw.text(SILVER_COORD, f"Nrs {int(silver_price)} / TOLA", fill=TEXT_COLOR_SILVER, font=font)

    img.save(FILENAME)
    print(f"[✅] Image saved as {FILENAME}")
except Exception as e:
    print(f"[ERROR] Image generation failed: {e}")

# === UPLOAD TO GOOGLE DRIVE ===
def upload_to_drive(service_account_file, folder_id, file_path):
    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds)

    filename = os.path.basename(file_path)

    # Search for file with same name in folder
    results = service.files().list(
        q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    items = results.get("files", [])

    media = MediaFileUpload(file_path, mimetype="image/png", resumable=True)

    if items:
        # File exists, update it
        file_id = items[0]["id"]
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        print("✅ File updated:", updated_file["id"])
    else:
        # File doesn't exist, create it
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        new_file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
        print("✅ File uploaded:", new_file["webViewLink"])

upload_to_drive(SERVICE_ACCOUNT_FILE, DRIVE_FOLDER_ID, FILENAME)
