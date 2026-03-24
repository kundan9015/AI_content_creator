"""
Thumbnail generator from video clips
"""
from pathlib import Path
from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import os

from config.settings import THUMBNAILS_DIR, THUMBNAIL_TIME, THUMBNAIL_QUALITY
from src.logger import logger


class ThumbnailGenerator:
    def __init__(self):
        self.thumbnail_time = THUMBNAIL_TIME
        self.quality = THUMBNAIL_QUALITY

    def generate_thumbnail(self, video_path: str, output_filename: str,
                          time_position: int = None) -> str:
        """
        Generate thumbnail from video at specified time

        Args:
            video_path: Path to video file
            output_filename: Output filename (e.g., "thumb_001.jpg")
            time_position: Time in seconds (default: THUMBNAIL_TIME)

        Returns:
            Path to generated thumbnail
        """
        if time_position is None:
            time_position = self.thumbnail_time

        output_path = THUMBNAILS_DIR / output_filename

        try:
            logger.info(f"Generating thumbnail: {output_filename}")

            with VideoFileClip(video_path) as video:
                # Ensure time position is within video duration
                if time_position >= video.duration:
                    time_position = video.duration / 2

                # Get frame at specified time
                frame = video.get_frame(time_position)

            # Convert to PIL Image
            image = Image.fromarray(frame)

            # Save thumbnail
            image.save(str(output_path), quality=self.quality, optimize=True)

            file_size_kb = output_path.stat().st_size / 1024
            logger.success(f"Thumbnail generated: {output_filename} ({file_size_kb:.2f} KB)")

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise

    def generate_thumbnail_with_text(self, video_path: str, output_filename: str,
                                    text: str, time_position: int = None) -> str:
        """
        Generate thumbnail with text overlay

        Args:
            video_path: Path to video file
            output_filename: Output filename
            text: Text to overlay on thumbnail
            time_position: Time in seconds

        Returns:
            Path to generated thumbnail
        """
        if time_position is None:
            time_position = self.thumbnail_time

        output_path = THUMBNAILS_DIR / output_filename

        try:
            logger.info(f"Generating thumbnail with text: {output_filename}")

            with VideoFileClip(video_path) as video:
                if time_position >= video.duration:
                    time_position = video.duration / 2

                frame = video.get_frame(time_position)

            # Convert to PIL Image
            image = Image.fromarray(frame)

            # Add text overlay
            draw = ImageDraw.Draw(image)

            # Calculate text size and position
            img_width, img_height = image.size

            # Try to load a font, fallback to default if not available
            try:
                font_size = int(img_height * 0.08)  # 8% of image height
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Position text at bottom center
            x = (img_width - text_width) / 2
            y = img_height - text_height - 40

            # Draw text background (semi-transparent black)
            padding = 20
            draw.rectangle(
                [x - padding, y - padding,
                 x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 180)
            )

            # Draw text
            draw.text((x, y), text, fill=(255, 255, 255), font=font)

            # Save thumbnail
            image.save(str(output_path), quality=self.quality, optimize=True)

            logger.success(f"Thumbnail with text generated: {output_filename}")

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating thumbnail with text: {str(e)}")
            # Fallback to simple thumbnail
            return self.generate_thumbnail(video_path, output_filename, time_position)

    def generate_multiple_thumbnails(self, video_path: str,
                                    output_prefix: str,
                                    count: int = 3) -> list:
        """
        Generate multiple thumbnails at different time positions

        Args:
            video_path: Path to video file
            output_prefix: Prefix for output filenames
            count: Number of thumbnails to generate

        Returns:
            List of paths to generated thumbnails
        """
        thumbnails = []

        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration

            # Calculate time positions
            interval = duration / (count + 1)
            time_positions = [int(interval * (i + 1)) for i in range(count)]

            for i, time_pos in enumerate(time_positions, 1):
                filename = f"{output_prefix}_{i}.jpg"
                thumb_path = self.generate_thumbnail(
                    video_path, filename, time_pos
                )
                thumbnails.append(thumb_path)

            logger.success(f"Generated {count} thumbnails")
            return thumbnails

        except Exception as e:
            logger.error(f"Error generating multiple thumbnails: {str(e)}")
            raise

    def cleanup_thumbnail(self, thumbnail_path: str):
        """Delete thumbnail file"""
        try:
            path = Path(thumbnail_path)
            if path.exists():
                path.unlink()
                logger.info(f"Cleaned up thumbnail: {path.name}")
        except Exception as e:
            logger.warning(f"Error cleaning up thumbnail: {str(e)}")
