"""
NepState Social Media Posting via Make.com Webhook
Sends video as multipart to Make.com which posts to Facebook + Instagram
"""

import requests
import os
from datetime import datetime

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")

def send_to_make(video_path, caption, video_type="gold"):
    """Send video to Make.com webhook as multipart upload"""
    if not MAKE_WEBHOOK_URL:
        print("⚠️  Make.com webhook URL not set — skipping")
        return False

    print(f"📤 Sending {video_type} video to Make.com...")

    try:
        file_size = os.path.getsize(video_path)
        file_name = os.path.basename(video_path)
        print(f"   Video size: {file_size / 1024:.1f} KB")
        print(f"   Sending to Make.com webhook...")

        with open(video_path, "rb") as f:
            res = requests.post(
                MAKE_WEBHOOK_URL,
                files={
                    "video": (file_name, f, "video/mp4")
                },
                data={
                    "caption": caption,
                    "video_type": video_type,
                    "file_name": file_name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
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
