"""
Local PC Agent - Runs on your PC and syncs with cloud dashboard
Handles video processing, Facebook uploads, and auto-delete
"""
import requests
import time
import json
import uuid
import socket
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database
from src.video_processor import VideoProcessor
from src.thumbnail_generator import ThumbnailGenerator
from src.caption_generator import CaptionGenerator
from src.uploader import FacebookUploader
from src.notifier import Notifier
from src.logger import logger
from config.settings import DELETE_CLIPS_AFTER_UPLOAD


class LocalAgent:
    def __init__(self, cloud_url):
        self.cloud_url = cloud_url.rstrip('/')
        self.pc_id = self.load_or_create_pc_id()
        self.pc_name = socket.gethostname()

        # Initialize components
        self.db = Database()
        self.video_processor = VideoProcessor()
        self.thumbnail_gen = ThumbnailGenerator()
        self.caption_gen = CaptionGenerator()
        self.uploader = FacebookUploader()
        self.notifier = Notifier()

        self.running = True
        self.check_interval = 60  # Check cloud every 60 seconds

        logger.info(f"Local Agent initialized")
        logger.info(f"PC ID: {self.pc_id}")
        logger.info(f"PC Name: {self.pc_name}")
        logger.info(f"Cloud URL: {self.cloud_url}")

    def load_or_create_pc_id(self):
        """Load or create unique PC ID"""
        pc_id_file = Path('local-agent/.pc_id')
        pc_id_file.parent.mkdir(exist_ok=True)

        if pc_id_file.exists():
            return pc_id_file.read_text().strip()
        else:
            pc_id = str(uuid.uuid4())
            pc_id_file.write_text(pc_id)
            return pc_id

    def register_with_cloud(self):
        """Register this PC with cloud dashboard"""
        try:
            response = requests.post(
                f"{self.cloud_url}/api/register",
                json={
                    'pc_id': self.pc_id,
                    'pc_name': self.pc_name
                },
                timeout=10
            )

            if response.status_code == 200:
                logger.success("✓ Registered with cloud dashboard")
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False

    def send_heartbeat(self):
        """Send status update to cloud"""
        try:
            # Get current status
            video = self.db.get_active_video()

            data = {
                'pc_id': self.pc_id,
                'current_video': video['file_name'] if video else None,
                'progress': 0,
                'total_clips': 0,
                'uploaded_clips': 0
            }

            if video:
                progress = self.db.get_video_progress(video['id'])
                total = video['total_clips']
                uploaded = progress.get('uploaded', 0)

                data.update({
                    'total_clips': total,
                    'uploaded_clips': uploaded,
                    'progress': int((uploaded / total) * 100) if total > 0 else 0
                })

            response = requests.post(
                f"{self.cloud_url}/api/heartbeat",
                json=data,
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.debug(f"Heartbeat error: {str(e)}")
            return False

    def check_commands(self):
        """Check for pending commands from cloud"""
        try:
            response = requests.get(
                f"{self.cloud_url}/api/commands/{self.pc_id}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                commands = data.get('commands', [])

                for cmd in commands:
                    self.execute_command(cmd)

        except Exception as e:
            logger.debug(f"Command check error: {str(e)}")

    def execute_command(self, cmd):
        """Execute a command from cloud"""
        command_id = cmd['id']
        command = cmd['command']
        data = json.loads(cmd['data']) if cmd['data'] else {}

        logger.info(f"Executing command: {command}")

        try:
            if command == 'download_video':
                success = self.download_and_process_video(data)

            elif command == 'upload_now':
                success = self.process_next_clip()

            elif command == 'update_settings':
                success = self.update_settings(data)

            else:
                logger.warning(f"Unknown command: {command}")
                success = False

            # Report result
            self.report_command_result(command_id, success)

        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            self.report_command_result(command_id, False)

    def download_and_process_video(self, data):
        """Download video from cloud and add to processing queue"""
        try:
            queue_id = data['queue_id']
            filename = data['filename']
            clip_duration = data.get('clip_duration', 10)

            logger.info(f"Downloading video: {filename}")

            # Download video
            response = requests.get(
                f"{self.cloud_url}/api/download-video/{queue_id}",
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                logger.error("Download failed")
                return False

            # Save video
            video_path = Path('data/videos') / filename
            video_path.parent.mkdir(parents=True, exist_ok=True)

            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.success(f"✓ Video downloaded: {filename}")

            # Add to database
            duration = self.video_processor.get_video_duration(str(video_path))
            video_id = self.db.add_video(
                file_name=filename,
                file_path=str(video_path.absolute()),
                duration_seconds=duration,
                clip_duration=clip_duration
            )

            logger.success(f"✓ Video added to queue (ID: {video_id})")

            # Cleanup cloud storage
            requests.post(
                f"{self.cloud_url}/api/cleanup-temp",
                json={'queue_id': queue_id},
                timeout=10
            )

            return True

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return False

    def process_next_clip(self):
        """Process and upload next pending clip"""
        try:
            # Get active video
            video = self.db.get_active_video()
            if not video:
                logger.info("No active video")
                return True

            # Get next clip
            clip = self.db.get_next_pending_clip(video['id'])
            if not clip:
                logger.info("All clips uploaded!")
                self.db.mark_video_complete(video['id'])
                return True

            clip_number = clip['clip_number']
            logger.info(f"Processing clip {clip_number}/{video['total_clips']}")

            # Generate clip
            logger.info("Generating video clip...")
            clip_filename = f"clip_{clip_number:03d}.mp4"
            clip_path = self.video_processor.generate_clip(
                video['file_path'],
                clip['start_time'],
                clip['end_time'],
                clip_filename
            )

            # Generate thumbnail
            logger.info("Generating thumbnail...")
            thumbnail_filename = f"thumb_{clip_number:03d}.jpg"
            thumbnail_path = self.thumbnail_gen.generate_thumbnail(
                clip_path,
                thumbnail_filename
            )

            # Generate caption
            logger.info("Generating caption...")
            caption = self.caption_gen.generate_caption(
                clip_number,
                video['total_clips'],
                video['file_name'],
                style='engaging'
            )

            # Update database
            self.db.update_clip_paths(
                clip['id'],
                clip_path,
                thumbnail_path,
                caption
            )

            # Upload to Facebook
            logger.info("Uploading to Facebook...")
            post_id = self.uploader.upload_video(
                clip_path,
                caption,
                thumbnail_path
            )

            if post_id:
                # Success!
                self.db.update_clip_status(clip['id'], 'uploaded', post_id)
                self.db.add_log(
                    'upload',
                    'success',
                    f"Clip {clip_number} uploaded",
                    f"Post ID: {post_id}"
                )

                logger.success(f"✓ Upload complete! Post ID: {post_id}")

                # Auto-delete if enabled
                if DELETE_CLIPS_AFTER_UPLOAD:
                    self.cleanup_files(clip_path, thumbnail_path)

                # Send notification
                self.notifier.notify_upload_success(
                    clip_number,
                    video['total_clips'],
                    post_id
                )

                return True
            else:
                # Failed
                self.db.update_clip_status(
                    clip['id'],
                    'failed',
                    error_message="Upload failed"
                )
                logger.error("Upload failed!")
                return False

        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return False

    def cleanup_files(self, clip_path, thumbnail_path):
        """Delete clip files to save space"""
        try:
            if Path(clip_path).exists():
                Path(clip_path).unlink()
                logger.info(f"Deleted: {Path(clip_path).name}")

            if Path(thumbnail_path).exists():
                Path(thumbnail_path).unlink()
                logger.info(f"Deleted: {Path(thumbnail_path).name}")

            logger.success("✓ Files cleaned up")

        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")

    def update_settings(self, settings):
        """Update local settings from cloud"""
        logger.info(f"Updating settings: {settings}")
        # TODO: Update local config file
        return True

    def report_command_result(self, command_id, success):
        """Report command execution result to cloud"""
        try:
            requests.post(
                f"{self.cloud_url}/api/command-result",
                json={
                    'command_id': command_id,
                    'success': success
                },
                timeout=10
            )
        except:
            pass

    def run(self):
        """Main agent loop"""
        logger.separator()
        logger.info("🚀 Local Agent Starting...")
        logger.separator()

        # Register with cloud
        if not self.register_with_cloud():
            logger.error("Failed to connect to cloud. Retrying...")
            time.sleep(5)
            return self.run()

        logger.info(f"✓ Connected to cloud: {self.cloud_url}")
        logger.info(f"⏰ Checking every {self.check_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        logger.separator()

        last_heartbeat = 0

        try:
            while self.running:
                current_time = time.time()

                # Send heartbeat every 30 seconds
                if current_time - last_heartbeat > 30:
                    self.send_heartbeat()
                    last_heartbeat = current_time

                # Check for commands
                self.check_commands()

                # Sleep
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n\nAgent stopped by user")
            self.running = False

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            logger.info("Restarting in 10 seconds...")
            time.sleep(10)
            return self.run()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Local PC Agent')
    parser.add_argument('--cloud-url', type=str,
                       help='Cloud dashboard URL')
    parser.add_argument('--register', action='store_true',
                       help='Register and exit')

    args = parser.parse_args()

    # Get cloud URL
    if args.cloud_url:
        cloud_url = args.cloud_url
    elif os.environ.get('CLOUD_URL'):
        cloud_url = os.environ.get('CLOUD_URL')
    else:
        # Try to load from config
        config_file = Path('local-agent/.config')
        if config_file.exists():
            cloud_url = config_file.read_text().strip()
        else:
            print("Error: Cloud URL not specified!")
            print("Usage:")
            print("  python agent.py --cloud-url https://your-app.onrender.com")
            print("Or set CLOUD_URL environment variable")
            sys.exit(1)

    # Save cloud URL for future use
    config_file = Path('local-agent/.config')
    config_file.parent.mkdir(exist_ok=True)
    config_file.write_text(cloud_url)

    # Create agent
    agent = LocalAgent(cloud_url)

    if args.register:
        # Just register and exit
        if agent.register_with_cloud():
            print(f"✓ Registered successfully!")
            print(f"PC ID: {agent.pc_id}")
            print(f"PC Name: {agent.pc_name}")
        else:
            print("✗ Registration failed!")
        sys.exit(0)

    # Run agent
    agent.run()


if __name__ == "__main__":
    main()
