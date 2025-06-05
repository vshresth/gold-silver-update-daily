from PIL import Image, ImageDraw, ImageFont
import requests
import json
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# === CONFIGURATION ===
API_URL = "https://keyvalue.hamropatro.com/kv/get/market_segment_gold::1690855810198"
TEMPLATE_IMAGE = "template.png"
FONT_PATH = "arial.ttf"
GOLD_COORD = (680, 980)
SILVER_COORD = (680, 1300)
FONT_SIZE = 75
TEXT_COLOR_GOLD = "#F5A623"
TEXT_COLOR_SILVER = "#B0B0B0"
FILENAME = "gold-price.png"  # Use a fixed filename for consistent Drive link

# === FETCH GOLD & SILVER PRICE ===
try:
    response = requests.get(API_URL)
    outer_json = response.json()
    value_str = outer_json["list"][0]["value"]
    data = json.loads(value_str)

    gold_price = None
    silver_price = None

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
        raise ValueError("Could not find gold or silver price in API response")

except Exception as e:
    print(f"[ERROR] Failed to get price data: {e}")
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
    print(f"[ERROR] Failed to generate image: {e}")

# === UPLOAD TO GOOGLE DRIVE ===
def upload_to_drive(filename):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Your folder ID from the Google Drive folder link
    folder_id = "1nD5OEXFN2S7QCucpF8xArTjY4aYN-bJO"

    # Check if file exists in that folder
    query = f"title='{filename}' and '{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        file = file_list[0]
    else:
        file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})

    file.SetContentFile(filename)
    file.Upload()
    print(f"[✅] Uploaded {filename} to folder {folder_id}")


upload_to_drive(FILENAME)
