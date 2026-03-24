# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
# Copy example config
cp .env.example .env

# Edit .env and add:
# - FACEBOOK_ACCESS_TOKEN
# - FACEBOOK_PAGE_ID
# - VIDEO_PATH
```

### 3. Initialize
```bash
python main.py --init
```

### 4. Add Video
```bash
python main.py --add-video data/videos/your_video.mp4
```

### 5. Test & Upload
```bash
# Test Facebook connection
python main.py --test-facebook

# Upload first clip manually
python main.py --upload-now

# Start automated daily uploads
python main.py --start-scheduler
```

## 📋 Essential Commands

```bash
# Check status
python main.py --status

# Preview next clip
python main.py --preview

# Manual upload
python main.py --upload-now
```

## 🔧 Troubleshooting

**Issue: FFmpeg not found**
```bash
# Windows
choco install ffmpeg

# Linux
sudo apt install ffmpeg
```

**Issue: Facebook error**
- Check token in .env
- Verify page ID
- Test: `python main.py --test-facebook`

## 📖 Full Documentation
See [README.md](README.md) for complete guide.
