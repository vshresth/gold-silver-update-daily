# gold-silver-update-daily
update gold and silver price daily in facebook and instragram for Nepstate
# 🌟 NepState Daily Gold/Silver Price Auto Poster

This project automatically fetches gold and silver prices from Hamro Patro API, generates a branded image using a Canva template, uploads it to Google Drive, and posts it daily to Instagram and Facebook using Buffer and Zapier.

---

## ✨ Features

* Fetches latest prices from Hamro Patro API
* Generates daily price image using Python (PIL)
* Uploads to Google Drive (fixed folder)
* Triggered daily via GitHub Actions (cron)
* Uses Zapier to post on social media

---

## 📂 Project Structure

```
NepState-Gold-Silver/
├── main.py
├── template.png
├── arial.ttf
├── client_secrets.json  # Google Drive API credentials
├── requirements.txt
├── .github/
│   └── workflows/
│       └── daily-run.yml
```

---

## 🚀 Setup from Scratch

### 1. Clone the Repo

```bash
git clone https://github.com/vshresth/gold-silver-update-daily.git
cd gold-silver-update-daily
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Google Drive Setup

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create new project
* Enable **Google Drive API**
* Create **OAuth Client ID** (Desktop app)
* Download `client_secrets.json` and place in root folder

### 4. Run Manually (Local Test)

```bash
python main.py
```

---

## ✨ GitHub Actions Automation

### 1. Create `.github/workflows/daily-run.yml`

```yaml
name: Daily Gold/Silver Image Generator
on:
  schedule:
    - cron: "0 10 * * *"  # 10 AM UTC daily
  workflow_dispatch:
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run script
        run: python main.py
```

### 2. Commit & Push

```bash
git add .
git commit -m "Initial automation setup"
git push origin main
```

---

## 🌐 Fly.io (optional cloud deploy)

### Commands used:

```bash
fly launch       # setup your app
fly deploy       # deploy code
fly logs         # view logs
fly apps list    # list apps
fly status       # app status
fly machines stop <id>
fly machines start <id>
```

---

## 🚪 Zapier Automation

### Zap 1: Auto-Post to Facebook + Instagram via Buffer

* **Trigger**: New File in Google Drive Folder
* **Action**: Add to Buffer

  * Connect Buffer
  * Select profiles (FB & IG)
  * Add caption, use image from Drive

### Zapier Notes:

* Free plan supports **3 zaps, 10 tasks/month**
* You can bypass scheduling since GitHub already runs daily
* Caption examples:

  ```
  ```

Today's Gold Price: Rs. 1,87,000 / tola
Silver Price: Rs. 2,300 / tola
\#goldprice #silverprice #Nepal #NepState

```

---

## 📁 Files
- **main.py**: Python script to fetch data, generate image, upload to Google Drive
- **requirements.txt**:
```

pillow
requests
google-api-python-client
google-auth-httplib2
google-auth-oauthlib

```

---

## ❓ Troubleshooting

### Image not uploading?
- Make sure `client_secrets.json` exists
- Check if image path or Drive folder ID is correct

### GitHub Action not running?
- Confirm `cron` is correct (UTC)
- Manually trigger with `workflow_dispatch`

---

## ✨ Future Improvements
- Add watermark
- Automatically post to Instagram Story (manual workaround)
- Add logging to Discord or Slack

---

For support or contributions, reach out at [nepstate.com](https://nepstate.com)

```
