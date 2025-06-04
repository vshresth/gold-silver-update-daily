from PIL import Image, ImageDraw, ImageFont
import requests
import json
from datetime import datetime

# === CONFIGURATION ===

API_URL = "https://keyvalue.hamropatro.com/kv/get/market_segment_gold::1690855810198"
TEMPLATE_IMAGE = "template.png"    # Your Canva image template
FONT_PATH = "arial.ttf"            # Or use any .ttf you include
GOLD_COORD = (680, 980)     # Below the GOLD line
SILVER_COORD = (680, 1300)  # Below the SILVER line
FONT_SIZE = 75              # Make text more bold/visible
TEXT_COLOR_GOLD = "#F5A623"
TEXT_COLOR_SILVER = "#B0B0B0"
today = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = f"daily-price-{today}.png"

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

    img.save(OUTPUT_PATH)
    print(f"[✅] Image saved as {OUTPUT_PATH}")

except Exception as e:
    print(f"[ERROR] Failed to generate image: {e}")
