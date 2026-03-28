# 🇳🇵 NepState Gold & Silver Video Pipeline — Setup Guide

## What This Does
Every morning at 8am Nepal Time, this pipeline:
1. Fetches gold & silver prices from Hamro Patro API
2. Generates a professional animated MP4 video (9:16 vertical)
3. Posts automatically to Instagram Reels + Facebook
4. Runs FREE on GitHub Actions — forever

---

## Files Changed
- `main.py` — Upgraded from image → animated video + direct social posting
- `requirements.txt` — Updated dependencies
- `.github/workflows/daily-run.yml` — Updated workflow

---

## ONE-TIME SETUP (15-20 minutes)

### Step 1: GitHub Secrets
Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Where to get it |
|-------------|----------------|
| `FB_ACCESS_TOKEN` | Meta Developer Dashboard (see Step 2) |
| `FB_PAGE_ID` | Your Facebook Page ID (see below) |
| `IG_USER_ID` | Instagram Business Account ID (see Step 2) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Your existing service_account.json contents |

**Get your Facebook Page ID:**
- Go to your Facebook Page
- Click About → scroll down → Page ID is shown

---

### Step 2: Meta Developer Setup (for Instagram + Facebook posting)

1. Go to https://developers.facebook.com
2. Create a new App → Business type
3. Add products: **Instagram Graph API** + **Pages API**
4. Go to Graph API Explorer
5. Select your App
6. Generate a Page Access Token:
   - Select your NepState Facebook Page
   - Add permissions: `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`
7. Click Generate Access Token
8. Copy the token → Add as `FB_ACCESS_TOKEN` secret

**Get Instagram User ID:**
```
https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_TOKEN
```
Find your Instagram Business Account ID from the response.

**⚠️ Important:** Convert your token to a Long-Lived Token (valid 60 days):
```
https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=YOUR_SHORT_TOKEN
```

---

### Step 3: Push Updated Files
```bash
git add .
git commit -m "Upgrade: image → animated video with direct social posting"
git push origin main
```

---

### Step 4: Test Manually
In your GitHub repo:
- Go to Actions tab
- Click "NepState Daily Gold & Silver Video"
- Click "Run workflow" → Run workflow
- Watch the logs
- Download the video artifact to preview it

---

## Posting Schedule
- **8:00 AM Nepal Time** = 2:15 AM UTC
- This means USA audience sees it in their evening (good for engagement)
- You can change the cron time in `.github/workflows/daily-run.yml`

**Cron time guide (change "15 2" to your preferred UTC time):**
| Nepal Time | UTC |
|------------|-----|
| 6:00 AM NPT | 0:15 UTC |
| 8:00 AM NPT | 2:15 UTC |
| 10:00 AM NPT | 4:15 UTC |
| 7:00 AM EST (USA) | 12:00 UTC |

---

## TikTok Setup (Coming Soon)
TikTok requires app review for auto-posting. For now:
1. Download the video artifact from GitHub Actions
2. Post manually to TikTok
3. Once you have 1000+ followers, apply for TikTok Content Posting API

---

## Troubleshooting

**Video not generating?**
- Check GitHub Actions logs
- Make sure FFmpeg installed correctly

**Instagram post failing?**
- Make sure your Instagram is a Business/Creator account
- Make sure it's connected to your Facebook Page
- Token may have expired — regenerate it

**Price showing N/A?**
- Hamro Patro API may be down — try again later
- Check your internet connection in the action logs

---

## Cost Breakdown
| Service | Cost |
|---------|------|
| GitHub Actions | FREE (2000 min/month) |
| Hamro Patro API | FREE |
| Meta Graph API | FREE |
| Google Drive | FREE |
| **Total** | **$0/month** |
