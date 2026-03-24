# AI Content Creator - Project Structure

## 📁 Directory Structure

```
ai_content_creator/
│
├── config/                      # Configuration files
│   ├── __init__.py
│   └── settings.py             # Application settings
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── database.py             # SQLite database handler
│   ├── video_processor.py     # Video splitting logic
│   ├── thumbnail_generator.py # Thumbnail generation
│   ├── caption_generator.py   # Caption generation
│   ├── uploader.py            # Facebook API uploader
│   ├── scheduler.py           # Daily scheduler
│   ├── notifier.py            # Email/Telegram notifications
│   └── logger.py              # Logging system
│
├── data/                       # Data directory
│   ├── videos/                # Input videos (place your videos here)
│   ├── clips/                 # Generated clips
│   ├── thumbnails/            # Generated thumbnails
│   └── database.db            # SQLite database (auto-created)
│
├── logs/                       # Log files (auto-created)
│   └── app_YYYYMMDD.log
│
├── tests/                      # Unit tests
│   └── test_basic.py
│
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Example configuration
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
├── setup.py                   # Setup script
├── main.py                    # Main entry point
├── examples.py                # Example usage
├── run_scheduler.bat          # Windows scheduler script
├── run_scheduler.sh           # Linux/Mac scheduler script
├── README.md                  # Complete documentation
├── QUICKSTART.md              # Quick start guide
├── CHANGELOG.md               # Version history
└── LICENSE                    # MIT License
```

## 📊 File Purposes

### Core Application Files

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Command-line interface and entry point | 300+ |
| `src/database.py` | Database operations and schema | 250+ |
| `src/video_processor.py` | Video splitting and processing | 200+ |
| `src/thumbnail_generator.py` | Thumbnail generation | 180+ |
| `src/caption_generator.py` | Caption and hashtag generation | 200+ |
| `src/uploader.py` | Facebook Graph API upload | 250+ |
| `src/scheduler.py` | Daily scheduling logic | 200+ |
| `src/notifier.py` | Email and Telegram alerts | 150+ |
| `src/logger.py` | Logging system | 80+ |

### Configuration Files

| File | Purpose |
|------|---------|
| `config/settings.py` | App configuration and constants |
| `.env` | Secret credentials (not in git) |
| `.env.example` | Template for .env file |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | 5-minute quick start |
| `CHANGELOG.md` | Version history |
| `examples.py` | Usage examples |

### Utility Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `setup.py` | Package installation |
| `.gitignore` | Git ignore patterns |
| `LICENSE` | MIT license |

## 🔄 Data Flow

```
1. Input Video
   └─> data/videos/movie.mp4

2. Video Processor
   └─> Splits into clips
       └─> data/clips/clip_001.mp4

3. Thumbnail Generator
   └─> Generates thumbnail
       └─> data/thumbnails/thumb_001.jpg

4. Caption Generator
   └─> Creates caption with hashtags

5. Facebook Uploader
   └─> Uploads to Facebook

6. Database
   └─> Records progress
       └─> data/database.db

7. Scheduler
   └─> Repeats daily automatically
```

## 💾 Database Schema

### Tables

**videos**
- id, file_name, file_path, duration_seconds
- clip_duration, total_clips, status
- added_at, completed_at

**clips**
- id, video_id, clip_number
- start_time, end_time, clip_path
- thumbnail_path, caption, status
- facebook_post_id, uploaded_at
- error_message, retry_count

**upload_schedule**
- id, video_id, scheduled_time
- last_run, next_run, is_active

**activity_logs**
- id, action, status, message
- details, timestamp

## 📦 Dependencies

### Required
- `moviepy` - Video processing
- `pillow` - Image processing
- `requests` - HTTP requests
- `python-dotenv` - Environment variables
- `schedule` - Job scheduling

### Optional
- `pytest` - Testing
- `black` - Code formatting

## 🚀 Entry Points

### Command Line
```bash
python main.py [command]
```

### Scheduler
```bash
python main.py --start-scheduler
```

### Windows Task Scheduler
```
run_scheduler.bat
```

## 🔐 Security

### Protected Files (not in git)
- `.env` - Contains secrets
- `data/database.db` - User data
- `data/videos/*` - User videos
- `data/clips/*` - Generated clips
- `logs/*.log` - Log files

### Public Files
- Source code
- Documentation
- Configuration templates
- Example scripts

## 📈 Performance

### File Size Estimates
- **High quality** (1920x1080): ~50MB per 10 min
- **Medium quality** (1280x720): ~25MB per 10 min
- **Low quality** (854x480): ~10MB per 10 min

### Processing Time Estimates
- Clip generation: 30-60 seconds per 10 min clip
- Thumbnail generation: 1-2 seconds
- Upload time: 30-120 seconds (depends on internet)
- Total: ~2-3 minutes per clip

### Storage Requirements
For 3-hour video (180 minutes):
- Original video: ~500 MB - 2 GB
- 18 clips (high): ~900 MB
- 18 thumbnails: ~5 MB
- Database: < 1 MB
- **Total**: ~1.5 GB - 3 GB

## 🛠️ Development

### Adding New Features

1. **New video source**: Modify `video_processor.py`
2. **New upload platform**: Create new uploader in `src/`
3. **Custom captions**: Edit `caption_generator.py`
4. **Different scheduling**: Modify `scheduler.py`

### Code Style
- Python 3.8+ features
- Type hints recommended
- Docstrings for all functions
- Clean, readable code
- Proper error handling

### Testing
```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_basic.py
```

## 📝 Maintenance

### Regular Tasks
- Renew Facebook access token (every 60 days)
- Check disk space
- Review error logs
- Update dependencies

### Backup
Important files to backup:
- `data/database.db`
- `.env`
- `config/settings.py` (if customized)

## 🎯 Future Enhancements

Potential improvements:
- [ ] Web dashboard (Flask/Streamlit)
- [ ] Multi-platform support (Instagram, YouTube)
- [ ] Better thumbnail selection (AI-based)
- [ ] Speech-to-text for captions
- [ ] Video analytics integration
- [ ] Batch processing
- [ ] Cloud storage integration
- [ ] Mobile notifications

---

**Total Lines of Code**: ~2000+
**Total Files**: 20+
**Development Time**: Production-ready
**Maintenance**: Minimal
