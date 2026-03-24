# 🎬 AI Content Creator - Automatic Video Clip Uploader & Facebook Scheduler

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A complete production-level system that automatically splits long videos into clips, generates thumbnails and captions, and uploads them to Facebook on a daily schedule - completely running on your local machine!

## ✨ Features

### Core Features
- ✅ **Automatic Video Splitting** - Split long videos (e.g., 3-hour movies) into sequential clips
- ✅ **Smart Progress Tracking** - SQLite database tracks upload progress
- ✅ **Thumbnail Generation** - Auto-generate thumbnails from video frames
- ✅ **AI-Style Captions** - Automatically generate engaging captions with hashtags
- ✅ **Facebook Upload** - Upload to Facebook using Graph API
- ✅ **Daily Scheduler** - Automated daily uploads at your chosen time
- ✅ **Error Handling** - Retry logic and comprehensive error handling

### Enhanced Features
- 🎨 **Multiple Video Quality** - High, medium, low quality presets
- 📧 **Email Notifications** - Get notified on upload success/failure
- 📱 **Telegram Notifications** - Real-time alerts via Telegram
- 📊 **Status Dashboard** - View progress and activity logs
- 🔄 **Resume Support** - Continue from where you left off
- 🧹 **Auto Cleanup** - Optional cleanup of clips after upload
- 🔍 **Preview Mode** - Test without actually uploading

## 📋 Table of Contents

- [Installation](#-installation)
- [Facebook Setup](#-facebook-setup-important)
- [Configuration](#%EF%B8%8F-configuration)
- [Usage](#-usage)
- [Scheduling](#-scheduling)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required by moviepy)
- Facebook Page with admin access
- Facebook App with access token

### Step 1: Install FFmpeg

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Or use chocolatey:
choco install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### Step 2: Clone or Download Project

```bash
cd /path/to/your/directory
# Project files should be in AI_content_creator/
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Initialize Project

```bash
python main.py --init
```

## 🔑 Facebook Setup (IMPORTANT!)

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Choose **"Business"** type
4. Fill in App Name and Contact Email
5. Click **"Create App"**

### Step 2: Add Facebook Login

1. In your app dashboard, click **"Add Product"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. Choose **"Web"** platform
4. Skip the quickstart

### Step 3: Get Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App from dropdown
3. Click **"Generate Access Token"**
4. Grant these permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `pages_manage_metadata`
5. Copy the **Access Token**

### Step 4: Get Page ID

**Method 1: Graph API Explorer**
```
/me/accounts
```
This will show all pages you manage with their IDs.

**Method 2: From Facebook Page**
1. Go to your Facebook Page
2. Click **"About"**
3. Scroll to **"Page ID"**

### Step 5: Extend Token (IMPORTANT!)

Short-lived tokens expire in 1 hour. Get a long-lived token (60 days):

```bash
# Replace YOUR_APP_ID, YOUR_APP_SECRET, and YOUR_SHORT_TOKEN
https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN
```

Copy the `access_token` from the response.

### Step 6: Get Never-Expiring Token (Optional)

For page tokens that never expire:

```bash
# Use your long-lived token
https://graph.facebook.com/me/accounts?access_token=YOUR_LONG_LIVED_TOKEN
```

Use the `access_token` for your page from the response.

## ⚙️ Configuration

### Step 1: Create .env file

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Step 2: Edit .env file

```env
# Facebook Configuration (REQUIRED)
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Video Configuration
VIDEO_PATH=data/videos/movie.mp4
CLIP_DURATION=10
VIDEO_QUALITY=high

# Schedule Configuration
UPLOAD_TIME=09:00
TIMEZONE=Asia/Kolkata

# Optional Settings
ENABLE_COMPRESSION=true
MAX_FILE_SIZE_MB=500
DELETE_CLIPS_AFTER_UPLOAD=false

# Email Notifications (Optional)
ENABLE_EMAIL_NOTIFICATIONS=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
NOTIFICATION_EMAIL=notification@gmail.com

# Telegram Notifications (Optional)
ENABLE_TELEGRAM_NOTIFICATIONS=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Configuration Options Explained

| Option | Description | Default |
|--------|-------------|---------|
| `CLIP_DURATION` | Clip length in minutes | 10 |
| `VIDEO_QUALITY` | Quality preset (high/medium/low) | high |
| `UPLOAD_TIME` | Daily upload time (24-hour format) | 09:00 |
| `ENABLE_COMPRESSION` | Compress videos | true |
| `MAX_FILE_SIZE_MB` | Max file size | 500 |

## 📖 Usage

### 1. Add Your Video

Place your video in `data/videos/` folder:

```bash
# Copy your video
cp /path/to/your/movie.mp4 data/videos/

# Add to database
python main.py --add-video data/videos/movie.mp4
```

**Output:**
```
✓ Video added successfully!
  Video ID: 1
  Duration: 10800 seconds (180 minutes)
  Total clips: 18
  Clip duration: 10 minutes
```

### 2. Test Facebook Connection

```bash
python main.py --test-facebook
```

**Expected Output:**
```
✓ Facebook credentials validated for: Your Page Name
✓ Connected to page: Your Page Name
  Fans: 1523
```

### 3. Preview Next Clip

```bash
python main.py --preview
```

**Output:**
```
📋 NEXT CLIP PREVIEW
Video: movie.mp4
Clip: 1/18
Time: 00:00:00 - 00:10:00
Duration: 10 minutes

Caption Preview:
------------------------------------------------------------
Part 1 of 18 🎬

👉 Follow for the next part!

#viral #trending #series #webseries #followforfollowback
------------------------------------------------------------
```

### 4. Upload Next Clip (Manual)

```bash
python main.py --upload-now
```

**Output:**
```
============================================================
Starting scheduled upload job at 2026-03-24 15:30:00
============================================================
INFO - Active video: movie.mp4
INFO - Processing clip 1/18
INFO - Step 1: Generating video clip...
✓ Clip generated: clip_001.mp4 (45.23 MB)
INFO - Step 2: Generating thumbnail...
✓ Thumbnail generated: thumb_001.jpg (234.56 KB)
INFO - Step 3: Generating caption...
INFO - Step 4: Validating Facebook credentials...
✓ Facebook credentials validated
INFO - Step 5: Uploading to Facebook...
✓ Video uploaded successfully! Post ID: 123456789_987654321
============================================================
✓ UPLOAD COMPLETE!
  Clip: 1/18
  Post ID: 123456789_987654321
============================================================
```

### 5. Check Status

```bash
python main.py --status
```

**Output:**
```
============================================================
📊 PROJECT STATUS
============================================================

📹 Video: movie.mp4
   Status: active
   Duration: 10800 seconds
   Total Clips: 18
   Uploaded: 5/18
   Pending: 13
   Failed: 0
   Next clip: 6

============================================================
📝 RECENT ACTIVITY (Last 10)
============================================================
✓ 2026-03-24 09:00:00 - upload: Clip 5 uploaded
✓ 2026-03-23 09:00:00 - upload: Clip 4 uploaded
✓ 2026-03-22 09:00:00 - upload: Clip 3 uploaded
============================================================
```

### 6. Start Scheduler

```bash
python main.py --start-scheduler
```

**Output:**
```
============================================================
🚀 AI Content Creator Scheduler Started
⏰ Daily upload scheduled at: 09:00
============================================================
Next upload: 2026-03-25 09:00:00
Press Ctrl+C to stop the scheduler
============================================================
```

## 📅 Scheduling

### Option 1: Python Scheduler (Simple)

Run the Python scheduler in background:

```bash
# Windows
run_scheduler.bat

# Linux/Mac
chmod +x run_scheduler.sh
./run_scheduler.sh
```

**Note:** PC must be running at scheduled time.

### Option 2: Windows Task Scheduler (Recommended)

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name: `AI Content Creator Upload`
4. Trigger: **Daily** at `09:00 AM`
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `main.py --upload-now`
   - Start in: `D:\AI_content_creator`
6. Finish

### Option 3: Linux Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/AI_content_creator && /usr/bin/python3 main.py --upload-now
```

## 🔧 Troubleshooting

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Install FFmpeg first
# Windows: choco install ffmpeg
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### Issue: "Facebook credentials validation failed"

**Solutions:**
1. Check if token is correct in `.env`
2. Token might be expired - generate new one
3. Check required permissions
4. Verify Page ID is correct

### Issue: "Video file not found"

**Solution:**
```bash
# Check video path in .env
# Make sure file exists
ls data/videos/

# Use absolute path if relative doesn't work
VIDEO_PATH=/full/path/to/video.mp4
```

### Issue: "Upload failed"

**Possible Causes:**
1. Internet connection issues
2. Video file too large (>4GB)
3. Facebook API rate limits
4. Invalid access token

**Solution:**
```bash
# Check logs
cat logs/app_YYYYMMDD.log

# Test connection
python main.py --test-facebook

# Try manual upload
python main.py --upload-now
```

### Issue: "MoviePy errors"

**Solution:**
```bash
# Reinstall moviepy
pip uninstall moviepy
pip install moviepy==1.0.3

# Install imageio-ffmpeg
pip install imageio-ffmpeg
```

## 📊 Command Reference

| Command | Description |
|---------|-------------|
| `--init` | Initialize project |
| `--add-video PATH` | Add video to queue |
| `--status` | Show current status |
| `--preview` | Preview next clip |
| `--test-facebook` | Test Facebook connection |
| `--test-notifications` | Test notifications |
| `--upload-now` | Upload next clip now |
| `--start-scheduler` | Start scheduler |

## 💡 Tips & Best Practices

1. **Test First**: Always test with a small video first
2. **Backup Database**: Keep backup of `data/database.db`
3. **Monitor Logs**: Check logs regularly in `logs/` folder
4. **Token Expiry**: Set calendar reminder for token renewal
5. **Disk Space**: Ensure enough space for clips
6. **Quality vs Size**: Use "medium" quality if "high" is too large
7. **Peak Hours**: Schedule uploads during peak audience hours

## 🎯 Example Workflow

```bash
# Day 1: Setup
python main.py --init
# Configure .env file
python main.py --test-facebook
python main.py --add-video data/videos/movie.mp4

# Day 1: Preview and test
python main.py --preview
python main.py --upload-now

# Day 1: Start automation
python main.py --start-scheduler
# OR setup Windows Task Scheduler

# Daily: Check status
python main.py --status
```

## 🔒 Security Notes

- Never commit `.env` file to Git
- Don't share access tokens
- Use app-specific passwords for email
- Keep Facebook App Secret secure
- Regularly rotate access tokens

## 📈 Scaling Up

### Multiple Videos

The system supports queuing multiple videos:

```bash
python main.py --add-video video1.mp4
python main.py --add-video video2.mp4
# System will process them one by one
```

### Multiple Upload Times

Edit scheduler code to add more times:

```python
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("18:00").do(job)
```

### Different Platforms

Extend the uploader to support:
- Instagram (modify `uploader.py`)
- YouTube (add YouTube API)
- Twitter/X (add Twitter API)

## 📝 FAQ

**Q: Can I change clip duration?**
A: Yes, change `CLIP_DURATION` in `.env` (in minutes)

**Q: What video formats are supported?**
A: MP4, AVI, MKV, MOV (any format supported by FFmpeg)

**Q: How to stop scheduler?**
A: Press `Ctrl+C` in terminal

**Q: Can I delete uploaded clips?**
A: Set `DELETE_CLIPS_AFTER_UPLOAD=true` in `.env`

**Q: Upload failed, what now?**
A: System auto-retries 3 times. Check logs for details.

**Q: Can I customize captions?**
A: Yes, edit templates in `src/caption_generator.py`

**Q: How to add more hashtags?**
A: Edit hashtag lists in `src/caption_generator.py`

**Q: What if video is shorter than clip duration?**
A: System automatically adjusts last clip duration

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- More caption templates
- Better thumbnail generation
- Multi-platform support
- Web dashboard
- API rate limit handling

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- MoviePy for video processing
- Facebook Graph API
- Python Schedule library

## 📞 Support

If you encounter issues:
1. Check troubleshooting section
2. Review logs in `logs/` folder
3. Test Facebook connection
4. Verify FFmpeg installation

---

**Made with ❤️ for content creators**

**Happy Uploading! 🚀**
