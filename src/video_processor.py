"""
Video processing module for splitting videos into clips
"""
from pathlib import Path
from typing import Tuple
from moviepy.editor import VideoFileClip
import os

from config.settings import (
    CLIPS_DIR, VIDEO_QUALITY_PRESETS, VIDEO_QUALITY,
    ENABLE_COMPRESSION, MAX_FILE_SIZE_MB
)
from src.logger import logger


class VideoProcessor:
    def __init__(self):
        self.quality = VIDEO_QUALITY_PRESETS.get(
            VIDEO_QUALITY,
            VIDEO_QUALITY_PRESETS["high"]
        )

    def get_video_duration(self, video_path: str) -> int:
        """Get video duration in seconds"""
        try:
            with VideoFileClip(video_path) as video:
                duration = int(video.duration)
            logger.info(f"Video duration: {duration} seconds ({duration // 60} minutes)")
            return duration
        except Exception as e:
            logger.error(f"Error reading video duration: {str(e)}")
            raise

    def validate_video_file(self, video_path: str) -> bool:
        """Validate if video file exists and is readable"""
        path = Path(video_path)

        if not path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False

        if not path.is_file():
            logger.error(f"Path is not a file: {video_path}")
            return False

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"Video file size: {file_size_mb:.2f} MB")

        return True

    def generate_clip(self, video_path: str, start_time: int,
                     end_time: int, output_filename: str) -> str:
        """
        Generate a video clip from start_time to end_time

        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_filename: Output filename (e.g., "clip_001.mp4")

        Returns:
            Path to generated clip
        """
        output_path = CLIPS_DIR / output_filename

        try:
            logger.info(f"Generating clip: {output_filename}")
            logger.info(f"Time range: {start_time}s to {end_time}s")

            with VideoFileClip(video_path) as video:
                # Extract clip
                clip = video.subclip(start_time, end_time)

                # Prepare codec settings
                codec_settings = {
                    'codec': 'libx264',
                    'audio_codec': 'aac',
                    'temp_audiofile': 'temp-audio.m4a',
                    'remove_temp': True,
                    'preset': 'medium',
                }

                # Add compression settings
                if ENABLE_COMPRESSION:
                    codec_settings['bitrate'] = self.quality['bitrate']
                    codec_settings['audio_bitrate'] = '128k'

                # Write clip
                clip.write_videofile(
                    str(output_path),
                    **codec_settings,
                    logger=None,  # Disable moviepy's logger
                    verbose=False,
                    threads=4
                )

                clip.close()

            # Check file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.success(f"Clip generated: {output_filename} ({file_size_mb:.2f} MB)")

            # Check if file exceeds max size
            if file_size_mb > MAX_FILE_SIZE_MB:
                logger.warning(f"Clip size exceeds {MAX_FILE_SIZE_MB} MB limit!")
                # Could implement further compression here

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating clip: {str(e)}")
            # Clean up partial file if exists
            if output_path.exists():
                output_path.unlink()
            raise

    def get_video_info(self, video_path: str) -> dict:
        """Get detailed video information"""
        try:
            with VideoFileClip(video_path) as video:
                info = {
                    'duration': video.duration,
                    'fps': video.fps,
                    'size': video.size,
                    'width': video.w,
                    'height': video.h,
                }
            return info
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    def format_time(self, seconds: int) -> str:
        """Format seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def cleanup_clip(self, clip_path: str):
        """Delete clip file to save disk space"""
        try:
            path = Path(clip_path)
            if path.exists():
                path.unlink()
                logger.info(f"Cleaned up clip: {path.name}")
        except Exception as e:
            logger.warning(f"Error cleaning up clip: {str(e)}")
