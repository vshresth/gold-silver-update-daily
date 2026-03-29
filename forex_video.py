"""
NepState Daily Forex Rate Video Generator
Fetches rates from Nepal Rastra Bank API, generates animated MP4, posts to social media.
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
# CONFIGURATION
# ============================================================
NRB_API = "https://www.nrb.org.np/api/forex/v1/rates?per_page=100&page=1&from={date}&to={date}"

FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
DURATION = 12
OUTPUT_VIDEO = "forex-rate.mp4"
FRAMES_DIR = "forex_frames"

# NepState dark premium colors
COLOR_BG_TOP       = (8, 12, 25)
COLOR_BG_BOTTOM    = (4, 6, 12)
COLOR_GOLD         = (212, 160, 23)
COLOR_GOLD_LIGHT   = (255, 210, 80)
COLOR_RED          = (192, 57, 43)
COLOR_WHITE        = (255, 255, 255)
COLOR_MUTED        = (140, 150, 170)
COLOR_GREEN        = (46, 184, 92)
COLOR_BLUE_CARD    = (12, 18, 40)
COLOR_CARD_BORDER  = (30, 45, 90)

# Currencies to show — matching NepState's existing forex posts
CURRENCIES = [
    {"iso3": "USD", "flag": "🇺🇸", "name": "U.S. Dollar",        "unit": 1},
    {"iso3": "EUR", "flag": "🇪🇺", "name": "European Euro",       "unit": 1},
    {"iso3": "GBP", "flag": "🇬🇧", "name": "UK Pound Sterling",   "unit": 1},
    {"iso3": "AUD", "flag": "🇦🇺", "name": "Australian Dollar",   "unit": 1},
    {"iso3": "CAD", "flag": "🇨🇦", "name": "Canadian Dollar",     "unit": 1},
    {"iso3": "CHF", "flag": "🇨🇭", "name": "Swiss Franc",         "unit": 1},
    {"iso3": "SGD", "flag": "🇸🇬", "name": "Singapore Dollar",    "unit": 1},
    {"iso3": "CNY", "flag": "🇨🇳", "name": "Chinese Yuan",        "unit": 1},
    {"iso3": "INR", "flag": "🇮🇳", "name": "Indian Rupee",        "unit": 100},
]

# ============================================================
# STEP 1: FETCH FOREX RATES FROM NRB
# ============================================================
def fetch_forex_rates():
    print("📡 Fetching forex rates from Nepal Rastra Bank...")
    from datetime import timezone, timedelta
    EST = timezone(timedelta(hours=-5))
    today = datetime.now(EST).strftime("%Y-%m-%d")
    url = NRB_API.format(date=today)
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        payload = data["data"]["payload"]
        if not payload:
            raise ValueError("Empty payload")
        rates_raw = payload[0]["rates"]
        rates = {}
        for r in rates_raw:
            iso3 = r["currency"]["iso3"]
            rates[iso3] = {
                "buy":  float(r["buy"]),
                "sell": float(r["sell"]),
                "unit": r["currency"]["unit"],
                "name": r["currency"]["name"]
            }
        print(f"✅ Fetched {len(rates)} currency rates")
        return rates, today
    except Exception as e:
        print(f"[ERROR] NRB API failed: {e}")
        return None, today

# ============================================================
# STEP 2: GENERATE VIDEO FRAMES
# ============================================================
def get_font(size, bold=False):
    """English font"""
    paths = [
        "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

def get_nepali_font(size, bold=False):
    """Nepali/Devanagari font"""
    paths = [
        "NotoSansDevanagari-Bold.ttf" if bold else "NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return get_font(size, bold)

def ease_out(t):
    return 1 - (1 - min(1.0, t)) ** 3

def lerp(a, b, t):
    return a + (b - a) * t

def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=1):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    for cx, cy in [(x1, y1), (x2-radius*2, y1), (x1, y2-radius*2), (x2-radius*2, y2-radius*2)]:
        draw.ellipse([cx, cy, cx+radius*2, cy+radius*2], fill=fill)
    if outline:
        draw.rectangle([x1+radius, y1, x2-radius, y1+outline_width], fill=outline)
        draw.rectangle([x1+radius, y2-outline_width, x2-radius, y2], fill=outline)
        draw.rectangle([x1, y1+radius, x1+outline_width, y2-radius], fill=outline)
        draw.rectangle([x2-outline_width, y1+radius, x2, y2-radius], fill=outline)

def draw_bg(img, frame_num, total_frames):
    draw = ImageDraw.Draw(img)
    progress = frame_num / total_frames
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        wave = math.sin(progress * math.pi * 2 + ratio * 4) * 3
        r = int(lerp(COLOR_BG_TOP[0], COLOR_BG_BOTTOM[0], ratio) + wave)
        g = int(lerp(COLOR_BG_TOP[1], COLOR_BG_BOTTOM[1], ratio) + wave)
        b = int(lerp(COLOR_BG_TOP[2], COLOR_BG_BOTTOM[2], ratio) + wave * 2)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b))))

def generate_frame(frame_num, total_frames, rates, today):
    progress = frame_num / total_frames
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLOR_BG_TOP)
    draw_bg(img, frame_num, total_frames)
    draw = ImageDraw.Draw(img)

    # Subtle grid pattern
    for x in range(0, VIDEO_WIDTH, 60):
        alpha_val = int(8 + 4 * math.sin(progress * math.pi + x * 0.05))
        draw.line([(x, 0), (x, VIDEO_HEIGHT)], fill=(30, 50, 100))
    for y in range(0, VIDEO_HEIGHT, 60):
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(20, 35, 70))

    # Top accent bar
    draw.rectangle([0, 0, VIDEO_WIDTH, 6], fill=COLOR_RED)

    # ── HEADER ──────────────────────────────────────────────
    h_t = ease_out(min(1.0, progress * 5))
    h_y = int(lerp(-150, 0, h_t))

    font_logo   = get_font(68, bold=True)
    font_sub    = get_font(28)
    font_title  = get_font(52, bold=True)
    font_date   = get_font(30)

    draw.text((540, 80 + h_y),  "NepState",                    font=font_logo,  fill=COLOR_GOLD,  anchor="mm")
    draw.text((540, 135 + h_y), "Connecting Nepalese Globally 🌏", font=font_sub, fill=COLOR_MUTED, anchor="mm")

    # Title
    t_t = ease_out(min(1.0, max(0, (progress - 0.05) * 5)))
    font_title_nep = get_nepali_font(46, bold=True)
    draw.text((540, 200 + h_y), "💱 विदेशी मुद्राको दर", font=font_title_nep, fill=COLOR_WHITE, anchor="mm")
    draw.text((540, 255 + h_y), "Forex Exchange Rates", font=font_title, fill=COLOR_GOLD_LIGHT, anchor="mm")
    draw.text((540, 300 + h_y), f"Nepal Rastra Bank • {today}", font=font_date,  fill=COLOR_MUTED,  anchor="mm")

    # Separator line
    sep_w = int(VIDEO_WIDTH * 0.85 * ease_out(min(1.0, max(0, (progress - 0.1) * 4))))
    sx = (VIDEO_WIDTH - sep_w) // 2
    draw.rectangle([sx, 300, sx + sep_w, 303], fill=COLOR_GOLD)

    # Column headers
    font_header = get_font(28, bold=True)
    header_t = ease_out(min(1.0, max(0, (progress - 0.12) * 4)))
    header_alpha = int(255 * header_t)
    draw.text((120, 325),  "CURRENCY",  font=font_header, fill=COLOR_MUTED, anchor="lm")
    draw.text((760, 325),  "BUY",       font=font_header, fill=COLOR_GREEN,  anchor="mm")
    draw.text((960, 325),  "SELL",      font=font_header, fill=COLOR_GOLD,   anchor="mm")
    draw.rectangle([60, 338, VIDEO_WIDTH-60, 340], fill=COLOR_CARD_BORDER)

    # ── CURRENCY ROWS ────────────────────────────────────────
    font_flag   = get_font(38)
    font_curr   = get_font(30, bold=True)
    font_curr_s = get_font(22)
    font_rate   = get_font(34, bold=True)

    row_h = 148
    start_y = 360
    card_pad = 40

    for i, curr in enumerate(CURRENCIES):
        iso3 = curr["iso3"]
        if iso3 not in rates:
            continue

        rate_data = rates[iso3]
        buy  = rate_data["buy"]
        sell = rate_data["sell"]
        unit = curr["unit"]

        # Staggered animation
        row_t = ease_out(min(1.0, max(0, (progress - 0.15 - i * 0.04) * 4)))
        row_x = int(lerp(-VIDEO_WIDTH, 0, row_t))
        y = start_y + i * row_h

        # Card background — alternate subtle shading
        card_color = (14, 22, 48) if i % 2 == 0 else (10, 16, 35)
        draw_rounded_rect(draw,
            [card_pad + row_x, y,
             VIDEO_WIDTH - card_pad + row_x, y + row_h - 8],
            radius=14, fill=card_color
        )

        # Left accent bar
        draw.rectangle([card_pad + row_x, y + 10,
                        card_pad + 4 + row_x, y + row_h - 18],
                       fill=COLOR_GOLD if i % 3 == 0 else COLOR_RED if i % 3 == 1 else COLOR_MUTED)

        # Flag
        draw.text((90 + row_x, y + row_h//2 - 4), curr["flag"],
                  font=font_flag, anchor="mm")

        # Currency name + ISO
        draw.text((200 + row_x, y + row_h//2 - 14),
                  curr["iso3"], font=font_curr, fill=COLOR_WHITE, anchor="lm")
        unit_label = f"(per {unit})" if unit > 1 else ""
        short_name = curr["name"].replace("Sterling", "").replace("Dollar", "").strip()
        draw.text((200 + row_x, y + row_h//2 + 16),
                  f"{short_name} {unit_label}".strip(),
                  font=font_curr_s, fill=COLOR_MUTED, anchor="lm")

        # Buy rate — green
        shimmer = int(8 * math.sin(progress * math.pi * 6 + i))
        buy_color = (min(255, COLOR_GREEN[0]+shimmer), min(255, COLOR_GREEN[1]+shimmer), COLOR_GREEN[2])
        draw.text((760 + row_x, y + row_h//2 - 4),
                  f"रू {buy:,.2f}", font=get_nepali_font(34, bold=True), fill=buy_color, anchor="mm")

        # Sell rate — gold
        sell_color = (min(255, COLOR_GOLD_LIGHT[0]+shimmer), min(255, COLOR_GOLD_LIGHT[1]+shimmer//2), COLOR_GOLD_LIGHT[2])
        draw.text((960 + row_x, y + row_h//2 - 4),
                  f"रू {sell:,.2f}", font=get_nepali_font(34, bold=True), fill=sell_color, anchor="mm")

    # ── FOOTER ───────────────────────────────────────────────
    footer_t = ease_out(min(1.0, max(0, (progress - 0.6) * 3)))
    f_y = int(lerp(VIDEO_HEIGHT + 100, 0, footer_t))
    fy = VIDEO_HEIGHT - 200 + f_y

    font_footer = get_font(34, bold=True)
    font_footer_s = get_font(26)
    font_hash = get_font(22)

    draw_rounded_rect(draw, [card_pad, fy, VIDEO_WIDTH-card_pad, fy+160],
                      radius=18, fill=(20, 10, 5))
    draw.text((540, fy+45), "🌐 nepstate.com", font=font_footer, fill=COLOR_RED, anchor="mm")
    draw.text((540, fy+90), "Business • Jobs • Events • Housing",
              font=font_footer_s, fill=COLOR_WHITE, anchor="mm")
    draw.text((540, fy+130),
              "#NepState #ForexNepal #ExchangeRates #NepaliUSA",
              font=font_hash, fill=COLOR_MUTED, anchor="mm")

    # Bottom bar
    draw.rectangle([0, VIDEO_HEIGHT-6, VIDEO_WIDTH, VIDEO_HEIGHT], fill=COLOR_RED)

    # Pulsing border
    pulse = int(2 + 2 * math.sin(progress * math.pi * 4))
    draw.rectangle([0, 0, VIDEO_WIDTH-1, VIDEO_HEIGHT-1], outline=COLOR_GOLD, width=pulse)

    return img

def generate_video(rates, today):
    print("🎬 Generating forex video frames...")
    os.makedirs(FRAMES_DIR, exist_ok=True)
    total_frames = FPS * DURATION
    for i in range(total_frames):
        frame = generate_frame(i, total_frames, rates, today)
        frame.save(f"{FRAMES_DIR}/frame_{i:04d}.png")
        if i % 30 == 0:
            print(f"   Frame {i}/{total_frames}...")
    print("🎞️ Compiling with FFmpeg...")
    music_file = "background_music.mp3"
    has_music = os.path.exists(music_file)
    
    if has_music:
        print("🎵 Adding background music...")
        cmd = ["ffmpeg", "-y", "-framerate", str(FPS),
               "-i", f"{FRAMES_DIR}/frame_%04d.png",
               "-stream_loop", "-1",
               "-i", music_file,
               "-c:v", "libx264", "-c:a", "aac",
               "-pix_fmt", "yuv420p", "-crf", "23",
               "-shortest",
               "-filter:a", "volume=0.3,afade=t=in:st=0:d=1,afade=t=out:st=11:d=1",
               "-movflags", "+faststart", OUTPUT_VIDEO]
    else:
        cmd = ["ffmpeg", "-y", "-framerate", str(FPS),
               "-i", f"{FRAMES_DIR}/frame_%04d.png",
               "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "23", "-movflags", "+faststart", OUTPUT_VIDEO]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] FFmpeg: {result.stderr}")
        return False
    print(f"✅ Forex video saved: {OUTPUT_VIDEO}")
    return True

# ============================================================
# STEP 3: POST TO FACEBOOK
# ============================================================
def post_to_facebook(video_path, today):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("⚠️  Facebook credentials not set — skipping")
        return False

    caption = f"""💱 आजको विदेशी मुद्राको दर | Forex Exchange Rates
📅 {today} | Nepal Rastra Bank

🇺🇸 USD • 🇪🇺 EUR • 🇬🇧 GBP • 🇦🇺 AUD
🇨🇦 CAD • 🇨🇭 CHF • 🇸🇬 SGD • 🇨🇳 CNY • 🇮🇳 INR

💡 Stay updated with daily rates!
🌐 Visit nepstate.com for more

#NepState #ForexNepal #ExchangeRates #NepaliUSA #NepalAmerica #NepaliCommunity #CurrencyRates #NPR #NepaliAbroad"""

    print("📤 Posting forex video to Facebook...")
    try:
        url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        with open(video_path, "rb") as vf:
            res = requests.post(url, data={"description": caption, "access_token": FB_ACCESS_TOKEN}, files={"file": vf})
        if res.json().get("id"):
            print("✅ Posted forex video to Facebook!")
            return True
        print(f"[ERROR] Facebook: {res.json()}")
        return False
    except Exception as e:
        print(f"[ERROR] Facebook post failed: {e}")
        return False

# ============================================================
# MAIN
# ============================================================
def cleanup():
    import shutil
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)

def main():
    print("=" * 50)
    print("💱 NepState Daily Forex Video Pipeline")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    rates, today = fetch_forex_rates()
    if not rates:
        print("❌ Could not fetch rates. Exiting.")
        sys.exit(1)

    success = generate_video(rates, today)
    if not success:
        print("❌ Video generation failed.")
        sys.exit(1)

    from social_post import send_to_make, generate_forex_caption
    caption = generate_forex_caption(today)
    fb_ok = send_to_make(OUTPUT_VIDEO, caption, "forex")

    cleanup()

    print("\n" + "=" * 50)
    print("📊 FOREX POSTING SUMMARY")
    print("=" * 50)
    print(f"  Facebook: {'✅ Posted' if fb_ok else '❌ Failed/Skipped'}")
    print("=" * 50)

if __name__ == "__main__":
    main()

# ============================================================
# OVERRIDE: Use new resumable upload posting  
# ============================================================
def post_forex_video(video_path, today):
    """New posting function using resumable upload"""
    from social_post import post_video_to_facebook, generate_forex_caption
    caption = generate_forex_caption(today)
    result = post_video_to_facebook(video_path, caption)
    return bool(result)
