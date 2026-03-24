"""
Scheduler for automated daily uploads
"""
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

from config.settings import UPLOAD_TIME, LOCK_FILE
from src.logger import logger
from src.database import Database
from src.video_processor import VideoProcessor
from src.thumbnail_generator import ThumbnailGenerator
from src.caption_generator import CaptionGenerator
from src.uploader import FacebookUploader
from src.notifier import Notifier


class Scheduler:
    def __init__(self):
        self.db = Database()
        self.video_processor = VideoProcessor()
        self.thumbnail_generator = ThumbnailGenerator()
        self.caption_generator = CaptionGenerator()
        self.uploader = FacebookUploader()
        self.notifier = Notifier()
        self.upload_time = UPLOAD_TIME

    def create_lock_file(self) -> bool:
        """Create lock file to prevent duplicate runs"""
        if LOCK_FILE.exists():
            logger.warning("Lock file exists. Another instance might be running.")
            return False

        try:
            LOCK_FILE.write_text(str(datetime.now()))
            return True
        except Exception as e:
            logger.error(f"Failed to create lock file: {str(e)}")
            return False

    def remove_lock_file(self):
        """Remove lock file"""
        try:
            if LOCK_FILE.exists():
                LOCK_FILE.unlink()
        except Exception as e:
            logger.error(f"Failed to remove lock file: {str(e)}")

    def process_and_upload_next_clip(self):
        """Main job: Process and upload next clip"""
        logger.separator()
        logger.info(f"Starting scheduled upload job at {datetime.now()}")
        logger.separator()

        # Create lock file
        if not self.create_lock_file():
            logger.error("Cannot acquire lock. Exiting.")
            return

        try:
            # Get active video
            video = self.db.get_active_video()

            if not video:
                logger.info("No active video found. Please add a video first.")
                self.remove_lock_file()
                return

            logger.info(f"Active video: {video['file_name']}")

            # Get next pending clip
            clip = self.db.get_next_pending_clip(video['id'])

            if not clip:
                logger.info("All clips uploaded!")
                self.db.mark_video_complete(video['id'])
                self.notifier.notify_video_complete(
                    video['file_name'],
                    video['total_clips']
                )
                self.remove_lock_file()
                return

            clip_number = clip['clip_number']
            logger.info(f"Processing clip {clip_number}/{video['total_clips']}")

            # Step 1: Generate video clip
            logger.info("Step 1: Generating video clip...")
            clip_filename = f"clip_{clip_number:03d}.mp4"

            clip_path = self.video_processor.generate_clip(
                video['file_path'],
                clip['start_time'],
                clip['end_time'],
                clip_filename
            )

            # Step 2: Generate thumbnail
            logger.info("Step 2: Generating thumbnail...")
            thumbnail_filename = f"thumb_{clip_number:03d}.jpg"

            thumbnail_path = self.thumbnail_generator.generate_thumbnail(
                clip_path,
                thumbnail_filename
            )

            # Step 3: Generate caption
            logger.info("Step 3: Generating caption...")
            caption = self.caption_generator.generate_caption(
                clip_number,
                video['total_clips'],
                video['file_name'],
                style='engaging'
            )

            # Update database with file paths
            self.db.update_clip_paths(
                clip['id'],
                clip_path,
                thumbnail_path,
                caption
            )

            # Step 4: Validate Facebook credentials
            logger.info("Step 4: Validating Facebook credentials...")
            if not self.uploader.validate_credentials():
                logger.error("Facebook credentials validation failed!")
                self.db.update_clip_status(clip['id'], 'failed',
                                          error_message="Invalid credentials")
                self.remove_lock_file()
                return

            # Step 5: Upload to Facebook
            logger.info("Step 5: Uploading to Facebook...")
            post_id = self.uploader.upload_video(
                clip_path,
                caption,
                thumbnail_path
            )

            if post_id:
                # Upload successful
                self.db.update_clip_status(clip['id'], 'uploaded', post_id)
                self.db.add_log(
                    'upload',
                    'success',
                    f"Clip {clip_number} uploaded",
                    f"Post ID: {post_id}"
                )

                # Send notification
                self.notifier.notify_upload_success(
                    clip_number,
                    video['total_clips'],
                    post_id
                )

                logger.separator()
                logger.success(f"UPLOAD COMPLETE!")
                logger.info(f"Clip: {clip_number}/{video['total_clips']}")
                logger.info(f"Post ID: {post_id}")
                logger.separator()

            else:
                # Upload failed
                self.db.update_clip_status(clip['id'], 'failed',
                                          error_message="Upload failed")
                self.db.add_log(
                    'upload',
                    'failed',
                    f"Clip {clip_number} upload failed",
                    ""
                )

                self.notifier.notify_upload_failure(
                    clip_number,
                    "Upload failed"
                )

                logger.error("Upload failed!")

            # Optional: Cleanup files to save space
            # self.video_processor.cleanup_clip(clip_path)
            # self.thumbnail_generator.cleanup_thumbnail(thumbnail_path)

        except Exception as e:
            logger.error(f"Error in upload job: {str(e)}")
            self.notifier.notify_error("Upload Job Error", str(e))

        finally:
            self.remove_lock_file()
            logger.separator()
            logger.info("Upload job completed")
            logger.separator()

    def start_scheduler(self):
        """Start the scheduler loop"""
        logger.separator()
        logger.info("🚀 AI Content Creator Scheduler Started")
        logger.info(f"⏰ Daily upload scheduled at: {self.upload_time}")
        logger.separator()

        # Schedule the job
        schedule.every().day.at(self.upload_time).do(
            self.process_and_upload_next_clip
        )

        # Calculate next run time
        next_run = schedule.next_run()
        logger.info(f"Next upload: {next_run}")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.separator()

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
            self.remove_lock_file()
            sys.exit(0)

        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.remove_lock_file()
            sys.exit(1)

    def run_once(self):
        """Run upload job once (manual trigger)"""
        logger.info("Running manual upload...")
        self.process_and_upload_next_clip()

    def get_schedule_info(self):
        """Get information about scheduled jobs"""
        jobs = schedule.get_jobs()

        if not jobs:
            logger.info("No scheduled jobs")
            return

        logger.info("Scheduled Jobs:")
        for job in jobs:
            logger.info(f"  - {job}")

        next_run = schedule.next_run()
        if next_run:
            logger.info(f"Next run: {next_run}")
