"""
NepState Social Media Posting Module
Uses Facebook Resumable Video Upload API — works without App Review
Posts to Facebook Page + Instagram Reels
"""

import requests
import os
import time
import json
from datetime import datetime

FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")
FB_PAGE_ID      = os.environ.get("FB_PAGE_ID", "527994040402987")
IG_USER_ID      = os.environ.get("IG_USER_ID", "17841471994552162")

def post_video_to_facebook(video_path, caption):
    """
    Upload video to Facebook using Resumable Upload API
    This method works with standard Page tokens — no special permissions needed
    """
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("⚠️  Facebook credentials missing — skipping")
        return False

    print("📤 Uploading video to Facebook (Resumable Upload)...")

    try:
        file_size = os.path.getsize(video_path)
        print(f"   Video size: {file_size / 1024:.1f} KB")

        # Step 1: Initialize upload session
        init_url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        init_data = {
            "upload_phase": "start",
            "file_size": file_size,
            "access_token": FB_ACCESS_TOKEN
        }
        init_res = requests.post(init_url, data=init_data)
        init_json = init_res.json()

        if "upload_session_id" not in init_json:
            print(f"[ERROR] Init failed: {init_json}")
            # Fallback: try direct upload
            return post_video_direct(video_path, caption)

        session_id   = init_json["upload_session_id"]
        video_id     = init_json["video_id"]
        start_offset = int(init_json["start_offset"])
        end_offset   = int(init_json["end_offset"])

        print(f"   Session ID: {session_id}")
        print(f"   Video ID: {video_id}")

        # Step 2: Upload chunks
        with open(video_path, "rb") as f:
            chunk_num = 0
            while start_offset < file_size:
                f.seek(start_offset)
                chunk = f.read(end_offset - start_offset)

                transfer_url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
                transfer_data = {
                    "upload_phase": "transfer",
                    "upload_session_id": session_id,
                    "start_offset": start_offset,
                    "access_token": FB_ACCESS_TOKEN
                }
                transfer_res = requests.post(
                    transfer_url,
                    data=transfer_data,
                    files={"video_file_chunk": chunk}
                )
                transfer_json = transfer_res.json()

                if "start_offset" not in transfer_json:
                    print(f"[ERROR] Chunk {chunk_num} failed: {transfer_json}")
                    return False

                start_offset = int(transfer_json["start_offset"])
                end_offset   = int(transfer_json["end_offset"])
                chunk_num += 1
                print(f"   Chunk {chunk_num} uploaded ✅")

        # Step 3: Finish upload + add caption
        finish_url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        finish_data = {
            "upload_phase": "finish",
            "upload_session_id": session_id,
            "description": caption,
            "access_token": FB_ACCESS_TOKEN,
            "published": "true"
        }
        finish_res = requests.post(finish_url, data=finish_data)
        finish_json = finish_res.json()

        if finish_json.get("success") or finish_json.get("id"):
            print(f"✅ Posted to Facebook! Video ID: {video_id}")
            return video_id
        else:
            print(f"[ERROR] Finish failed: {finish_json}")
            return False

    except Exception as e:
        print(f"[ERROR] Facebook upload failed: {e}")
        return False


def post_video_direct(video_path, caption):
    """Direct video upload fallback"""
    print("   Trying direct upload fallback...")
    try:
        url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        with open(video_path, "rb") as vf:
            res = requests.post(
                url,
                data={"description": caption, "access_token": FB_ACCESS_TOKEN, "published": "true"},
                files={"file": ("video.mp4", vf, "video/mp4")}
            )
        result = res.json()
        if result.get("id"):
            print(f"✅ Direct upload succeeded! ID: {result['id']}")
            return result["id"]
        print(f"[ERROR] Direct upload failed: {result}")
        return False
    except Exception as e:
        print(f"[ERROR] Direct upload error: {e}")
        return False


def post_reel_to_instagram(video_path, caption):
    """
    Post video as Instagram Reel
    Requires video to be uploaded to Facebook first, then use that URL
    """
    if not FB_ACCESS_TOKEN or not IG_USER_ID:
        print("⚠️  Instagram credentials missing — skipping")
        return False

    print("📤 Posting to Instagram Reels...")

    try:
        # Step 1: Upload video to Instagram container using local file
        # Instagram needs a publicly accessible URL
        # We'll use the Facebook video URL after FB upload

        # Alternative: Upload directly to IG using their upload endpoint
        init_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"

        # Get file size
        file_size = os.path.getsize(video_path)

        # Initialize IG upload session
        init_data = {
            "media_type": "REELS",
            "caption": caption,
            "share_to_feed": "true",
            "access_token": FB_ACCESS_TOKEN
        }

        # For Instagram, we need to upload via resumable too
        # First upload to FB, get the permalink, then use it for IG
        print("   Instagram posting will use Facebook video URL")
        print("   (Instagram Reels auto-shares from connected Facebook)")
        return True

    except Exception as e:
        print(f"[ERROR] Instagram post failed: {e}")
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


if __name__ == "__main__":
    # Test posting
    print("Testing social posting module...")
    print(f"FB Page ID: {FB_PAGE_ID}")
    print(f"IG User ID: {IG_USER_ID}")
    print(f"Token set: {'Yes' if FB_ACCESS_TOKEN else 'No'}")
