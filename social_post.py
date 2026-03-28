"""
NepState Social Media Posting via Make.com Webhook
Sends video + caption to Make.com which posts to Facebook + Instagram
"""

import requests
import os
import base64
from datetime import datetime

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")

def send_to_make(video_path, caption, video_type="gold"):
    """Send video to Make.com webhook for posting to Facebook + Instagram"""
    if not MAKE_WEBHOOK_URL:
        print("⚠️  Make.com webhook URL not set — skipping")
        return False

    print(f"📤 Sending {video_type} video to Make.com...")

    try:
        # Read video and encode as base64
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")

        file_name = os.path.basename(video_path)

        payload = {
            "video_data": video_b64,
            "caption": caption,
            "file_name": file_name,
            "video_type": video_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"   Video size: {len(video_bytes) / 1024:.1f} KB")
        print(f"   Sending to Make.com webhook...")

        res = requests.post(
            MAKE_WEBHOOK_URL,
            json=payload,
            timeout=120
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
