"""
NepState Social Media Posting via Make.com Webhook
Uploads video to GitHub Releases (public URL) then sends URL to Make.com
"""

import requests
import os
import base64
from datetime import datetime

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
GITHUB_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO      = "vshresth/gold-silver-update-daily"

def upload_to_transfer_sh(video_path, video_type="gold"):
    """Upload video to transfer.sh - free, public, no auth needed"""
    print("📦 Uploading video to transfer.sh for public URL...")
    try:
        file_name = os.path.basename(video_path)
        with open(video_path, "rb") as f:
            res = requests.put(
                f"https://transfer.sh/{file_name}",
                data=f,
                headers={"Max-Days": "1"},
                timeout=120
            )
        if res.status_code == 200:
            public_url = res.text.strip()
            print(f"✅ Video uploaded! Public URL: {public_url}")
            return public_url
        else:
            print(f"[ERROR] transfer.sh failed: {res.status_code} {res.text}")
            return None
    except Exception as e:
        print(f"[ERROR] transfer.sh upload failed: {e}")
        return None


def send_to_make(video_path, caption, video_type="gold"):
    """Upload video to GitHub then send URL to Make.com"""
    if not MAKE_WEBHOOK_URL:
        print("⚠️  Make.com webhook URL not set — skipping")
        return False

    # Step 1: Get public URL via GitHub Release
    video_url = upload_to_transfer_sh(video_path, video_type)
    if not video_url:
        print("[ERROR] Could not get public video URL")
        return False

    # Step 2: Send URL + caption to Make.com
    print(f"📤 Sending video URL to Make.com...")
    try:
        payload = {
            "video_url": video_url,
            "caption": caption,
            "video_type": video_type,
            "file_name": os.path.basename(video_path),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        res = requests.post(
            MAKE_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        if res.status_code == 200:
            print(f"✅ Successfully sent to Make.com! Response: {res.text}")
            return True
        else:
            print(f"[ERROR] Make.com webhook failed: {res.status_code} — {res.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to send to Make.com: {e}")
        return False


def generate_gold_caption(gold_price, silver_price):
    today = datetime.now().strftime("%B %d, %Y")
    return f"""🥇 आजको सुन र चाँदीको मूल्य | Today's Gold & Silver Rate
📅 {today}

🏅 सुन (Gold - HalMark): NPR {gold_price:,} / Tola
🥈 चाँदी (Silver): NPR {silver_price:,} / Tola

💡 Check live rates daily on nepstate.com
📌 Find Nepali businesses, jobs & events near you!
🌐 www.nepstate.com

👇 Tag someone who checks gold prices daily!
#NepState #GoldPrice #SilverPrice #SunakoMol #NepaliUSA #NepalDiaspora #GoldRate #NepaliCommunity #ConnectingNepaleseGlobally #HamroNepal"""


def generate_forex_caption(today):
    return f"""💱 आजको विदेशी मुद्राको दर | Forex Exchange Rates
📅 {today} | Nepal Rastra Bank Official Rates

🇺🇸 USD • 🇪🇺 EUR • 🇬🇧 GBP • 🇦🇺 AUD
🇨🇦 CAD • 🇨🇭 CHF • 🇸🇬 SGD • 🇨🇳 CNY • 🇮🇳 INR

💡 Stay updated with official NRB rates daily!
🌐 Visit nepstate.com for more updates

📌 Save this post for quick reference!
#NepState #ForexNepal #ExchangeRates #NepaliUSA #NepaliCommunity #CurrencyRates #NPR #NepaliAbroad #NepalRastraBank #NepaliDiaspora"""
