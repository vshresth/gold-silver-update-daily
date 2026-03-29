"""
NepState Daily Gold & Silver Price Video Generator
Fetches prices from Hamro Patro API, generates animated MP4 video,
posts directly to Instagram, Facebook, and TikTok.
"""

from PIL import Image, ImageDraw, ImageFont
import requests
import json
from datetime import datetime
import os
import sys
import subprocess
import math

# ============================================================
# CONFIGURATION — Store all secrets in GitHub Actions Secrets
# ============================================================

# Hamro Patro API (your existing one)
API_URL = "https://keyvalue.hamropatro.com/kv/get/market_segment_gold::1690855810198"

# Meta (Instagram + Facebook) — set these in GitHub Secrets
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")

# TikTok — set in GitHub Secrets
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 vertical for Reels/TikTok
FPS = 30
DURATION = 10  # seconds
OUTPUT_VIDEO = "gold-silver-price.mp4"
FRAMES_DIR = "frames"

# Colors (NepState brand)
COLOR_BG_TOP = (26, 20, 10)
COLOR_BG_BOTTOM = (10, 8, 4)
COLOR_GOLD = (212, 160, 23)
COLOR_GOLD_LIGHT = (255, 215, 80)
COLOR_SILVER = (192, 192, 210)
COLOR_SILVER_LIGHT = (230, 230, 255)
COLOR_RED = (192, 57, 43)
COLOR_WHITE = (255, 255, 255)
COLOR_MUTED = (160, 150, 130)

# ============================================================
# STEP 1: FETCH GOLD & SILVER PRICES
# ============================================================

def fetch_prices():
    print("📡 Fetching gold & silver prices from Hamro Patro...")
    try:
        response = requests.get(API_URL, timeout=10)
        outer_json = response.json()
        value_str = outer_json["list"][0]["value"]
        data = json.loads(value_str)

        gold_price = silver_price = None
        gold_24k = gold_22k = None

        for item in data["items"]:
            if item["name"] == "HalMark Gold":
                for p in item["prices"]:
                    if p["name"] == "1 tola":
                        gold_price = int(p["price"]["price"])
                    if p["name"] == "10 gram":
                        gold_24k = int(p["price"]["price"])
            if item["name"] == "Silver":
                for p in item["prices"]:
                    if p["name"] == "1 tola":
                        silver_price = int(p["price"]["price"])

        if not gold_price or not silver_price:
            raise ValueError("Missing price data")

        print(f"✅ Gold: NPR {gold_price:,} | Silver: NPR {silver_price:,}")
        return gold_price, silver_price, gold_24k

    except Exception as e:
        print(f"[ERROR] Price fetch failed: {e}")
        return None, None, None


# ============================================================
# STEP 2: GENERATE ANIMATED VIDEO FRAMES
# ============================================================

def ease_in_out(t):
    """Smooth easing function for animations"""
    return t * t * (3 - 2 * t)

def ease_out(t):
    return 1 - (1 - t) ** 3

def lerp(a, b, t):
    return a + (b - a) * t

def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)

def draw_gradient_bg(img, frame_num, total_frames):
    """Draw animated dark gradient background"""
    draw = ImageDraw.Draw(img)
    progress = frame_num / total_frames

    # Subtle animated gradient
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        # Slight animation
        anim = math.sin(progress * math.pi * 2 + ratio * 3) * 0.05

        r = int(lerp(COLOR_BG_TOP[0], COLOR_BG_BOTTOM[0], ratio) + anim * 10)
        g = int(lerp(COLOR_BG_TOP[1], COLOR_BG_BOTTOM[1], ratio) + anim * 8)
        b = int(lerp(COLOR_BG_TOP[2], COLOR_BG_BOTTOM[2], ratio) + anim * 5)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

def draw_decorative_elements(img, draw, frame_num, total_frames):
    """Draw animated decorative circles and lines"""
    progress = frame_num / total_frames

    # Animated glowing circles
    for i in range(3):
        phase = progress * math.pi * 2 + i * (math.pi * 2 / 3)
        alpha = int(15 + 10 * math.sin(phase))
        x = int(540 + 300 * math.cos(phase * 0.3 + i))
        y = int(960 + 200 * math.sin(phase * 0.2 + i))
        size = 200 + int(50 * math.sin(phase * 0.5))

        overlay = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        color = COLOR_GOLD if i == 0 else (COLOR_SILVER if i == 1 else COLOR_RED)
        ov_draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(*color, alpha)
        )
        img_rgba = img.convert('RGBA')
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        img.paste(img_rgba.convert('RGB'))

    # Horizontal separator lines
    for y_pos in [680, 1380]:
        for x in range(0, VIDEO_WIDTH, 4):
            alpha = int(40 + 20 * math.sin(progress * math.pi * 4 + x * 0.01))
            draw.line([(x, y_pos), (x + 2, y_pos)], fill=(*COLOR_GOLD, alpha) if len(COLOR_GOLD) == 3 else COLOR_GOLD)

def get_font(size, bold=False):
    """Get English font"""
    font_paths = [
        "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

def get_nepali_font(size, bold=False):
    """Get Nepali/Devanagari font"""
    font_paths = [
        "NotoSansDevanagari-Bold.ttf" if bold else "NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return get_font(size, bold)

def generate_frame(frame_num, total_frames, gold_price, silver_price, gold_24k):
    """Generate a single video frame"""
    progress = frame_num / total_frames
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLOR_BG_TOP)

    # Background gradient
    draw_gradient_bg(img, frame_num, total_frames)
    draw = ImageDraw.Draw(img)

    # Decorative elements
    draw_decorative_elements(img, draw, frame_num, total_frames)

    from datetime import timezone, timedelta
    EST = timezone(timedelta(hours=-5))  # EST (UTC-5)
    now_est = datetime.now(EST)
    today = now_est.strftime("%B %d, %Y")  # e.g. March 29, 2026 in EST

    # ── HEADER SECTION ──────────────────────────────────────
    # Logo area slide in from top
    header_t = min(1.0, progress * 4)
    header_t = ease_out(header_t)
    header_y = int(lerp(-200, 0, header_t))

    # Red accent bar at top
    draw.rectangle([0, header_y, VIDEO_WIDTH, header_y + 8], fill=COLOR_RED)

    # NepState logo text
    font_logo = get_font(72, bold=True)
    font_logo_sub = get_font(32)
    draw.text((540, header_y + 80), "NepState", font=font_logo,
              fill=COLOR_GOLD, anchor="mm")
    draw.text((540, header_y + 140), "Connecting Nepalese Globally 🌏",
              font=font_logo_sub, fill=COLOR_MUTED, anchor="mm")

    # Date
    font_date = get_font(36)
    draw.text((540, header_y + 200), f"📅  {today}",
              font=font_date, fill=COLOR_WHITE, anchor="mm")

    # Title
    font_title = get_font(58, bold=True)
    title_t = min(1.0, max(0, (progress - 0.1) * 5))
    title_t = ease_out(title_t)
    title_alpha = int(255 * title_t)
    draw.text((540, 410), "आजको सुन-चाँदीको भाउ", font=get_nepali_font(52, bold=True),
              fill=COLOR_GOLD, anchor="mm")
    draw.text((540, 480), "Today's Gold & Silver Rate", font=font_title,
              fill=COLOR_WHITE, anchor="mm")

    # ── GOLD SECTION ────────────────────────────────────────
    gold_t = min(1.0, max(0, (progress - 0.15) * 4))
    gold_t = ease_out(gold_t)
    gold_x = int(lerp(-VIDEO_WIDTH, 0, gold_t))

    # Gold card background
    card_padding = 40
    draw_rounded_rect(draw,
        [card_padding + gold_x, 560,
         VIDEO_WIDTH - card_padding + gold_x, 900],
        radius=24,
        fill=(40, 30, 5)
    )

    # Gold card border
    for thickness in range(3):
        draw.rectangle(
            [card_padding + thickness + gold_x, 560 + thickness,
             VIDEO_WIDTH - card_padding - thickness + gold_x, 900 - thickness],
            outline=(*COLOR_GOLD, 150),
            width=1
        )

    # Gold emoji + label
    font_metal = get_font(52, bold=True)
    font_price_big = get_font(90, bold=True)
    font_unit = get_font(34)
    font_sub = get_font(30)

    draw.text((150 + gold_x, 620), "🥇", font=get_font(60), anchor="mm")
    draw.text((400 + gold_x, 605), "GOLD (Halmark)", font=font_metal,
              fill=COLOR_GOLD_LIGHT, anchor="lm")
    draw.text((400 + gold_x, 650), "तोला / Tola", font=get_nepali_font(30), fill=COLOR_MUTED, anchor="lm")
              fill=COLOR_MUTED, anchor="lm")

    # Price with shimmer animation
    shimmer = int(20 * math.sin(progress * math.pi * 6))
    price_color = (
        min(255, COLOR_GOLD_LIGHT[0] + shimmer),
        min(255, COLOR_GOLD_LIGHT[1] + shimmer // 2),
        COLOR_GOLD_LIGHT[2]
    )
    price_text = f"NPR {gold_price:,}"
    draw.text((540 + gold_x, 790), price_text, font=font_price_big,
              fill=price_color, anchor="mm")

    if gold_24k:
        draw.text((540 + gold_x, 865), f"10g = NPR {gold_24k:,}",
                  font=font_sub, fill=COLOR_MUTED, anchor="mm")

    # ── SILVER SECTION ──────────────────────────────────────
    silver_t = min(1.0, max(0, (progress - 0.25) * 4))
    silver_t = ease_out(silver_t)
    silver_x = int(lerp(VIDEO_WIDTH, 0, silver_t))

    # Silver card
    draw_rounded_rect(draw,
        [card_padding + silver_x, 950,
         VIDEO_WIDTH - card_padding + silver_x, 1250],
        radius=24,
        fill=(15, 18, 30)
    )
    for thickness in range(3):
        draw.rectangle(
            [card_padding + thickness + silver_x, 950 + thickness,
             VIDEO_WIDTH - card_padding - thickness + silver_x, 1250 - thickness],
            outline=(*COLOR_SILVER, 130),
            width=1
        )

    draw.text((150 + silver_x, 1010), "🥈", font=get_font(60), anchor="mm")
    draw.text((400 + silver_x, 995), "SILVER", font=font_metal,
              fill=COLOR_SILVER_LIGHT, anchor="lm")
    draw.text((400 + silver_x, 1040), "तोला / Tola", font=font_sub,
              fill=COLOR_MUTED, anchor="lm")

    silver_shimmer = int(15 * math.sin(progress * math.pi * 6 + 1))
    silver_color = (
        min(255, COLOR_SILVER_LIGHT[0] + silver_shimmer),
        min(255, COLOR_SILVER_LIGHT[1] + silver_shimmer),
        min(255, COLOR_SILVER_LIGHT[2] + silver_shimmer)
    )
    draw.text((540 + silver_x, 1140), f"NPR {silver_price:,}",
              font=font_price_big, fill=silver_color, anchor="mm")
    draw.text((540 + silver_x, 1215), "per tola • चाँदी", font=get_nepali_font(30), fill=COLOR_MUTED, anchor="mm") #
              font=font_sub, fill=COLOR_MUTED, anchor="mm")

    # ── CURRENCY HINT ────────────────────────────────────────
    currency_t = min(1.0, max(0, (progress - 0.4) * 3))
    currency_t = ease_out(currency_t)
    cy_alpha = int(255 * currency_t)

    font_currency = get_font(34)
    usd_gold = gold_price / 133  # approx NPR to USD
    draw.text((540, 1310), f"≈ USD {usd_gold:,.0f} per tola",
              font=font_currency, fill=COLOR_MUTED, anchor="mm")

    # ── FOOTER ───────────────────────────────────────────────
    footer_t = min(1.0, max(0, (progress - 0.5) * 3))
    footer_t = ease_out(footer_t)
    footer_y = int(lerp(VIDEO_HEIGHT + 200, 0, footer_t))

    # Footer card
    draw_rounded_rect(draw,
        [card_padding, 1380 + footer_y,
         VIDEO_WIDTH - card_padding, 1640 + footer_y],
        radius=20,
        fill=(30, 10, 8)
    )

    font_footer_title = get_font(38, bold=True)
    font_footer_body = get_font(30)
    font_hashtag = get_font(26)

    draw.text((540, 1430 + footer_y), "🏢 List Your Nepali Business FREE",
              font=font_footer_title, fill=COLOR_GOLD, anchor="mm")
    draw.text((540, 1490 + footer_y), "Jobs • Events • Housing • Forum",
              font=font_footer_body, fill=COLOR_WHITE, anchor="mm")
    draw.text((540, 1540 + footer_y), "🌐 nepstate.com",
              font=font_footer_title, fill=COLOR_RED, anchor="mm")

    # Hashtags
    hashtags = "#NepState #GoldPrice #SunakoMol #Nepal #Nepali"
    draw.text((540, 1600 + footer_y), hashtags,
              font=font_hashtag, fill=COLOR_MUTED, anchor="mm")

    # Bottom red bar
    draw.rectangle([0, VIDEO_HEIGHT - 8, VIDEO_WIDTH, VIDEO_HEIGHT], fill=COLOR_RED)

    # ── PULSING BORDER ───────────────────────────────────────
    pulse = int(3 + 2 * math.sin(progress * math.pi * 4))
    draw.rectangle([0, 0, VIDEO_WIDTH - 1, VIDEO_HEIGHT - 1],
                   outline=COLOR_GOLD, width=pulse)

    return img


def generate_video(gold_price, silver_price, gold_24k):
    """Generate all frames and compile into MP4"""
    print("🎬 Generating video frames...")
    os.makedirs(FRAMES_DIR, exist_ok=True)

    total_frames = FPS * DURATION

    for i in range(total_frames):
        frame = generate_frame(i, total_frames, gold_price, silver_price, gold_24k)
        frame.save(f"{FRAMES_DIR}/frame_{i:04d}.png")
        if i % 30 == 0:
            print(f"   Frame {i}/{total_frames}...")

    print("🎞️ Compiling video with FFmpeg...")
    
    # Check if background music exists
    music_file = "background_music.mp3"
    has_music = os.path.exists(music_file)
    
    if has_music:
        print("🎵 Adding background music...")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", f"{FRAMES_DIR}/frame_%04d.png",
            "-stream_loop", "-1",
            "-i", music_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            "-shortest",
            "-filter:a", "volume=0.3,afade=t=in:st=0:d=1,afade=t=out:st=9:d=1",
            "-movflags", "+faststart",
            OUTPUT_VIDEO
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", f"{FRAMES_DIR}/frame_%04d.png",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            "-movflags", "+faststart",
            OUTPUT_VIDEO
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] FFmpeg failed: {result.stderr}")
        return False

    print(f"✅ Video saved: {OUTPUT_VIDEO}")
    return True


# ============================================================
# STEP 3: POST TO INSTAGRAM (via Meta Graph API)
# ============================================================

def post_to_instagram(video_path, gold_price, silver_price):
    """Post video to Instagram Reels via Meta Graph API"""
    if not FB_ACCESS_TOKEN or not IG_USER_ID:
        print("⚠️  Instagram credentials not set — skipping")
        return False

    today = datetime.now().strftime("%B %d, %Y")
    caption = f"""🥇 Today's Gold & Silver Rate | {today}

सुनको मूल्य (Gold Price):
NPR {gold_price:,} per Tola

चाँदीको मूल्य (Silver Price):
NPR {silver_price:,} per Tola

📌 Find Nepali businesses, jobs & events near you!
🌐 Visit nepstate.com

#NepState #GoldPrice #SilverPrice #SunakoMol #NepaliUSA #NepalDiaspora #HamroPatro #GoldRate #NepaliCommunity #ConnectingNepaleseGlobally"""

    print("📤 Uploading to Instagram...")
    try:
        # Step 1: Initialize upload
        init_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
        init_data = {
            "media_type": "REELS",
            "video_url": video_path,  # Must be public URL — see notes
            "caption": caption,
            "share_to_feed": True,
            "access_token": FB_ACCESS_TOKEN
        }
        init_res = requests.post(init_url, data=init_data)
        container_id = init_res.json().get("id")

        if not container_id:
            print(f"[ERROR] Instagram container failed: {init_res.json()}")
            return False

        # Step 2: Publish
        import time
        time.sleep(30)  # Wait for processing
        pub_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        pub_data = {
            "creation_id": container_id,
            "access_token": FB_ACCESS_TOKEN
        }
        pub_res = requests.post(pub_url, data=pub_data)
        if pub_res.json().get("id"):
            print("✅ Posted to Instagram Reels!")
            return True
        else:
            print(f"[ERROR] Instagram publish failed: {pub_res.json()}")
            return False

    except Exception as e:
        print(f"[ERROR] Instagram post failed: {e}")
        return False


# ============================================================
# STEP 4: POST TO FACEBOOK (via Meta Graph API)
# ============================================================

def post_to_facebook(video_path, gold_price, silver_price):
    """Post video to Facebook Page"""
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("⚠️  Facebook credentials not set — skipping")
        return False

    today = datetime.now().strftime("%B %d, %Y")
    caption = f"""🥇 आजको सुन र चाँदीको मूल्य | Today's Gold & Silver Rate
📅 {today}

🏅 सुन (Gold - HalMark): NPR {gold_price:,} / Tola
🥈 चाँदी (Silver): NPR {silver_price:,} / Tola

💡 Nepali businesses, jobs, events & housing listings near you!
🌐 www.nepstate.com — Connecting Nepalese Globally

👇 Tag a friend who checks gold prices daily!

#NepState #GoldPrice #SilverPrice #NepaliUSA #NepalAmerica #NepaliCommunity #SunakoMol #GoldRate"""

    print("📤 Posting to Facebook...")
    try:
        url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        data = {
            "description": caption,
            "access_token": FB_ACCESS_TOKEN,
        }
        with open(video_path, "rb") as video_file:
            files = {"file": video_file}
            res = requests.post(url, data=data, files=files)

        if res.json().get("id"):
            print("✅ Posted to Facebook!")
            return True
        else:
            print(f"[ERROR] Facebook post failed: {res.json()}")
            return False

    except Exception as e:
        print(f"[ERROR] Facebook post failed: {e}")
        return False


# ============================================================
# STEP 5: UPLOAD VIDEO TO CLOUD (for Instagram URL requirement)
# ============================================================

def upload_to_drive_and_get_url(video_path):
    """Upload video to Google Drive and get shareable URL"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        SERVICE_ACCOUNT_FILE = "service_account.json"
        DRIVE_FOLDER_ID = "1nD5OEXFN2S7QCucpF8xArTjY4aYN-bJO"

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        filename = os.path.basename(video_path)

        # Remove old file if exists
        results = service.files().list(
            q=f"name='{filename}' and '{DRIVE_FOLDER_ID}' in parents and trashed=false",
            fields='files(id, name)'
        ).execute()
        for f in results.get("files", []):
            service.files().delete(fileId=f["id"]).execute()

        # Upload new file
        file_metadata = {
            "name": filename,
            "parents": [DRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        new_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        file_id = new_file["id"]

        # Make publicly accessible
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        public_url = f"https://drive.google.com/uc?id={file_id}"
        print(f"✅ Video uploaded to Drive: {public_url}")
        return public_url

    except Exception as e:
        print(f"[ERROR] Drive upload failed: {e}")
        return None


# ============================================================
# MAIN — Run everything
# ============================================================

def cleanup_frames():
    """Remove frame images to save space"""
    import shutil
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
        print("🧹 Cleaned up frames")

def main():
    print("=" * 50)
    print("🇳🇵 NepState Daily Gold/Silver Video Pipeline")
    print(f"⏰ Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. Fetch prices
    gold_price, silver_price, gold_24k = fetch_prices()
    if not gold_price:
        print("❌ Could not fetch prices. Exiting.")
        sys.exit(1)

    # 2. Generate video
    success = generate_video(gold_price, silver_price, gold_24k)
    if not success:
        print("❌ Video generation failed. Exiting.")
        sys.exit(1)

    # 3. Upload to Drive (get public URL for Instagram)
    video_url = upload_to_drive_and_get_url(OUTPUT_VIDEO)

    # 4. Send to Make.com for posting to Facebook + Instagram
    from social_post import send_to_make, generate_gold_caption
    caption = generate_gold_caption(gold_price, silver_price)
    make_result = send_to_make(OUTPUT_VIDEO, caption, "gold")
    results = {
        "make_webhook": make_result,
        "facebook": make_result,
        "instagram": make_result,
    }

    # 5. Cleanup
    cleanup_frames()

    # 6. Summary
    print("\n" + "=" * 50)
    print("📊 POSTING SUMMARY")
    print("=" * 50)
    for platform, success in results.items():
        status = "✅ Posted" if success else "❌ Failed/Skipped"
        print(f"  {platform.capitalize()}: {status}")
    print(f"\n🥇 Gold: NPR {gold_price:,}/tola")
    print(f"🥈 Silver: NPR {silver_price:,}/tola")
    print("=" * 50)


if __name__ == "__main__":
    main()

# ============================================================
# OVERRIDE: Use new resumable upload posting
# ============================================================
def post_gold_silver(video_path, gold_price, silver_price):
    """New posting function using resumable upload"""
    from social_post import post_video_to_facebook, generate_gold_caption
    caption = generate_gold_caption(gold_price, silver_price)
    result = post_video_to_facebook(video_path, caption)
    return bool(result)
