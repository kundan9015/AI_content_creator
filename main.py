"""
Main entry point for AI Content Creator
"""
import sys
import argparse
from pathlib import Path

from src.database import Database
from src.video_processor import VideoProcessor
from src.uploader import FacebookUploader
from src.scheduler import Scheduler
from src.notifier import Notifier
from src.logger import logger
from config.settings import VIDEO_PATH


def init_project():
    """Initialize project (create database, check setup)"""
    logger.info("Initializing AI Content Creator...")

    # Create database
    db = Database()
    logger.success("Database initialized")

    # Check if .env file exists
    if not Path(".env").exists():
        logger.warning(".env file not found!")
        logger.info("Please copy .env.example to .env and configure it")
        logger.info("cp .env.example .env")
        return False

    logger.success("Project initialized successfully!")
    return True


def add_video(video_path: str = None):
    """Add a new video to the queue"""
    if not video_path:
        video_path = VIDEO_PATH

    video_file = Path(video_path)

    if not video_file.exists():
        logger.error(f"Video file not found: {video_path}")
        return False

    logger.info(f"Adding video: {video_file.name}")

    # Get video duration
    processor = VideoProcessor()

    if not processor.validate_video_file(video_path):
        return False

    duration = processor.get_video_duration(video_path)

    # Add to database
    db = Database()
    from config.settings import CLIP_DURATION

    video_id = db.add_video(
        video_file.name,
        str(video_file.absolute()),
        duration,
        CLIP_DURATION
    )

    total_clips = (duration // (CLIP_DURATION * 60)) + 1

    logger.success(f"Video added successfully!")
    logger.info(f"Video ID: {video_id}")
    logger.info(f"Duration: {duration} seconds ({duration // 60} minutes)")
    logger.info(f"Total clips: {total_clips}")
    logger.info(f"Clip duration: {CLIP_DURATION} minutes")

    db.add_log('video_added', 'success', f"Added {video_file.name}", f"ID: {video_id}")

    return True


def show_status():
    """Show current status of videos and clips"""
    db = Database()

    logger.separator()
    logger.info("📊 PROJECT STATUS")
    logger.separator()

    # Get all videos
    videos = db.get_all_videos()

    if not videos:
        logger.info("No videos found. Add a video first using:")
        logger.info("python main.py --add-video path/to/video.mp4")
        return

    for video in videos:
        logger.info(f"\n📹 Video: {video['file_name']}")
        logger.info(f"   Status: {video['status']}")
        logger.info(f"   Duration: {video['duration_seconds']} seconds")
        logger.info(f"   Total Clips: {video['total_clips']}")
        logger.info(f"   Uploaded: {video.get('uploaded_clips', 0)}/{video['total_clips']}")

        # Get progress
        progress = db.get_video_progress(video['id'])
        logger.info(f"   Pending: {progress.get('pending', 0)}")
        logger.info(f"   Failed: {progress.get('failed', 0)}")

        if video['status'] == 'active':
            next_clip = db.get_next_pending_clip(video['id'])
            if next_clip:
                logger.info(f"   Next clip: {next_clip['clip_number']}")

    logger.separator()

    # Recent logs
    logger.info("\n📝 RECENT ACTIVITY (Last 10)")
    logger.separator()

    logs = db.get_recent_logs(10)
    for log in logs:
        status_icon = "✓" if log['status'] == 'success' else "✗"
        logger.info(f"{status_icon} {log['timestamp']} - {log['action']}: {log['message']}")

    logger.separator()


def preview_next():
    """Preview next clip to be uploaded"""
    db = Database()

    video = db.get_active_video()
    if not video:
        logger.info("No active video found")
        return

    clip = db.get_next_pending_clip(video['id'])
    if not clip:
        logger.info("All clips uploaded!")
        return

    processor = VideoProcessor()
    from src.caption_generator import CaptionGenerator

    caption_gen = CaptionGenerator()

    logger.separator()
    logger.info("📋 NEXT CLIP PREVIEW")
    logger.separator()

    logger.info(f"Video: {video['file_name']}")
    logger.info(f"Clip: {clip['clip_number']}/{video['total_clips']}")
    logger.info(f"Time: {processor.format_time(clip['start_time'])} - {processor.format_time(clip['end_time'])}")
    logger.info(f"Duration: {(clip['end_time'] - clip['start_time']) // 60} minutes")

    # Preview caption
    caption = caption_gen.generate_caption(
        clip['clip_number'],
        video['total_clips'],
        video['file_name'],
        style='engaging'
    )

    logger.info(f"\nCaption Preview:")
    logger.info("-" * 60)
    print(caption)
    logger.info("-" * 60)

    logger.separator()


def test_facebook():
    """Test Facebook connection"""
    logger.info("Testing Facebook connection...")

    uploader = FacebookUploader()

    if uploader.test_connection():
        logger.success("Facebook connection test passed!")
        return True
    else:
        logger.error("Facebook connection test failed!")
        logger.info("\nPlease check:")
        logger.info("1. FACEBOOK_ACCESS_TOKEN is set correctly in .env")
        logger.info("2. FACEBOOK_PAGE_ID is set correctly in .env")
        logger.info("3. Access token has not expired")
        logger.info("4. Token has required permissions")
        return False


def test_notifications():
    """Test notification system"""
    notifier = Notifier()
    notifier.test_notifications()


def upload_now():
    """Upload next clip immediately"""
    scheduler = Scheduler()
    scheduler.run_once()


def start_scheduler():
    """Start the scheduler"""
    scheduler = Scheduler()
    scheduler.start_scheduler()


def reset_progress():
    """Reset upload progress (dangerous!)"""
    logger.warning("⚠️ This will reset all progress!")
    response = input("Are you sure? Type 'yes' to confirm: ")

    if response.lower() == 'yes':
        db = Database()
        # This is a simple implementation - you might want to add more logic
        logger.info("Reset functionality - implement based on requirements")
        logger.warning("Not implemented yet for safety")
    else:
        logger.info("Reset cancelled")


def main():
    parser = argparse.ArgumentParser(
        description="AI Content Creator - Automated Video Clip Uploader"
    )

    parser.add_argument('--init', action='store_true',
                       help='Initialize the project')
    parser.add_argument('--add-video', type=str, metavar='PATH',
                       help='Add a video to the queue')
    parser.add_argument('--status', action='store_true',
                       help='Show current status')
    parser.add_argument('--preview', action='store_true',
                       help='Preview next clip')
    parser.add_argument('--test-facebook', action='store_true',
                       help='Test Facebook connection')
    parser.add_argument('--test-notifications', action='store_true',
                       help='Test notification system')
    parser.add_argument('--upload-now', action='store_true',
                       help='Upload next clip immediately')
    parser.add_argument('--start-scheduler', action='store_true',
                       help='Start the scheduler')
    parser.add_argument('--reset', action='store_true',
                       help='Reset upload progress (use with caution!)')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Execute commands
    if args.init:
        init_project()

    elif args.add_video:
        add_video(args.add_video)

    elif args.status:
        show_status()

    elif args.preview:
        preview_next()

    elif args.test_facebook:
        test_facebook()

    elif args.test_notifications:
        test_notifications()

    elif args.upload_now:
        upload_now()

    elif args.start_scheduler:
        start_scheduler()

    elif args.reset:
        reset_progress()


if __name__ == "__main__":
    main()
