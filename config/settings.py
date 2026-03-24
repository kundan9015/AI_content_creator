"""
Configuration settings for AI Content Creator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
CLIPS_DIR = DATA_DIR / "clips"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
LOGS_DIR = BASE_DIR / "logs"
DATABASE_PATH = DATA_DIR / "database.db"

# Ensure directories exist
for directory in [DATA_DIR, VIDEOS_DIR, CLIPS_DIR, THUMBNAILS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Facebook Configuration
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_API_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

# Video Configuration
VIDEO_PATH = os.getenv("VIDEO_PATH", "data/videos/movie.mp4")
CLIP_DURATION = int(os.getenv("CLIP_DURATION", 10))  # minutes
VIDEO_QUALITY = os.getenv("VIDEO_QUALITY", "high")

# Quality presets
VIDEO_QUALITY_PRESETS = {
    "high": {"bitrate": "5000k", "resolution": (1920, 1080)},
    "medium": {"bitrate": "2500k", "resolution": (1280, 720)},
    "low": {"bitrate": "1000k", "resolution": (854, 480)}
}

# Upload Configuration
UPLOAD_TIME = os.getenv("UPLOAD_TIME", "09:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# Advanced Settings
ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 500))
DELETE_CLIPS_AFTER_UPLOAD = os.getenv("DELETE_CLIPS_AFTER_UPLOAD", "false").lower() == "true"

# Notifications
ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")

ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "false").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Thumbnail Configuration
THUMBNAIL_TIME = 5  # seconds from start
THUMBNAIL_QUALITY = 95

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds

# Lock file (prevent duplicate runs)
LOCK_FILE = BASE_DIR / "scheduler.lock"
