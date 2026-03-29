"""
NepState Social Media Posting via Make.com Webhook
Uploads video to Cloudinary (permanent public URL) then sends to Make.com
"""

import requests
import os
import hashlib
import time
from datetime import datetime

MAKE_WEBHOOK_URL        = os.environ.get("MAKE_WEBHOOK_URL", "")
CLOUDINARY_CLOUD_NAME   = os.environ.get("CLOUDINARY_CLOUD_NAME", "dmspt2mwy")
CLOUDINARY_API_KEY      = os.environ.get("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET   = os.environ.get("CLOUDINARY_API_SECRET", "")


def upload_to_cloudinary(video_path, video_type="gold"):
    """Upload video to Cloudinary — permanent public URL, Facebook compatible"""
    print("☁️  Uploading video to Cloudinary...")
    try:
        import hmac
        timestamp = str(int(time.time()))
        public_id = f"nepstate_{video_type}_{datetime.now().strftime('%Y%m%d')}"

        # Generate signature
        params_to_sign = f"public_id={public_id}&timestamp={timestamp}"
        signature = hashlib.sha1(
            f"{params_to_sign}{CLOUDINARY_API_SECRET}".encode()
        ).hexdigest()

        url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/video/upload"

        with open(video_path, "rb") as f:
            res = requests.post(url, data={
                "api_key":   CLOUDINARY_API_KEY,
                "timestamp": timestamp,
                "public_id": public_id,
                "signature": signature,
                "overwrite": "true",
                "resource_type": "video"
            }, files={"file": f}, timeout=120)

        if res.status_code == 200:
            data = res.json()
            public_url = data["secure_url"]
            print(f"✅ Cloudinary upload success! URL: {public_url}")
            return public_url
        else:
            print(f"[ERROR] Cloudinary failed: {res.status_code} — {res.text[:200]}")
            return None

    except Exception as e:
        print(f"[ERROR] Cloudinary upload failed: {e}")
        return None


def send_to_make(video_path, caption, video_type="gold"):
    """Upload to Cloudinary then send public URL to Make.com"""
    if not MAKE_WEBHOOK_URL:
        print("⚠️  Make.com webhook URL not set — skipping")
        return False

    # Step 1: Upload to Cloudinary
    video_url = upload_to_cloudinary(video_path, video_type)
    if not video_url:
        print("[ERROR] Could not get Cloudinary URL")
        return False

    # Step 2: Send to Make.com
    print(f"📤 Sending to Make.com...")
    try:
        payload = {
            "video_url": video_url,
            "caption":   caption,
            "video_type": video_type,
            "file_name": os.path.basename(video_path),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        res = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=30)
        if res.status_code == 200:
            print(f"✅ Sent to Make.com! Response: {res.text}")
            return True
        else:
            print(f"[ERROR] Make.com failed: {res.status_code} — {res.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Make.com send failed: {e}")
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
