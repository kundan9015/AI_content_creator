"""
Example usage script showing how to use the AI Content Creator
"""

from src.database import Database
from src.video_processor import VideoProcessor
from src.caption_generator import CaptionGenerator
from src.thumbnail_generator import ThumbnailGenerator
from src.uploader import FacebookUploader
from src.logger import logger


def example_add_video():
    """Example: Add a video to the database"""
    print("\n=== Example: Add Video ===")

    db = Database()
    processor = VideoProcessor()

    video_path = "data/videos/movie.mp4"

    # Get video duration
    duration = processor.get_video_duration(video_path)

    # Add to database
    video_id = db.add_video(
        file_name="movie.mp4",
        file_path=video_path,
        duration_seconds=duration,
        clip_duration=10  # 10 minutes
    )

    print(f"Video added with ID: {video_id}")


def example_generate_clip():
    """Example: Generate a video clip"""
    print("\n=== Example: Generate Clip ===")

    processor = VideoProcessor()

    video_path = "data/videos/movie.mp4"
    start_time = 0  # 0 seconds
    end_time = 600  # 10 minutes (600 seconds)

    clip_path = processor.generate_clip(
        video_path,
        start_time,
        end_time,
        "example_clip.mp4"
    )

    print(f"Clip generated: {clip_path}")


def example_generate_thumbnail():
    """Example: Generate thumbnail"""
    print("\n=== Example: Generate Thumbnail ===")

    thumbnail_gen = ThumbnailGenerator()

    thumbnail_path = thumbnail_gen.generate_thumbnail(
        video_path="data/clips/example_clip.mp4",
        output_filename="example_thumb.jpg",
        time_position=5  # 5 seconds into the video
    )

    print(f"Thumbnail generated: {thumbnail_path}")


def example_generate_caption():
    """Example: Generate caption"""
    print("\n=== Example: Generate Caption ===")

    caption_gen = CaptionGenerator()

    # Simple caption
    caption1 = caption_gen.generate_caption(
        clip_number=1,
        total_clips=18,
        style='simple'
    )
    print(f"Simple caption:\n{caption1}\n")

    # Engaging caption
    caption2 = caption_gen.generate_caption(
        clip_number=1,
        total_clips=18,
        video_name="My Awesome Movie",
        style='engaging'
    )
    print(f"Engaging caption:\n{caption2}\n")


def example_upload_to_facebook():
    """Example: Upload to Facebook"""
    print("\n=== Example: Upload to Facebook ===")

    uploader = FacebookUploader()

    # Test connection first
    if uploader.test_connection():
        print("Connection successful!")

        # Upload video
        post_id = uploader.upload_video(
            video_path="data/clips/example_clip.mp4",
            caption="This is a test upload from AI Content Creator",
            thumbnail_path="data/thumbnails/example_thumb.jpg"
        )

        if post_id:
            print(f"Upload successful! Post ID: {post_id}")
        else:
            print("Upload failed!")
    else:
        print("Connection failed!")


def example_database_queries():
    """Example: Database queries"""
    print("\n=== Example: Database Queries ===")

    db = Database()

    # Get active video
    video = db.get_active_video()
    if video:
        print(f"Active video: {video['file_name']}")

        # Get next pending clip
        clip = db.get_next_pending_clip(video['id'])
        if clip:
            print(f"Next clip: {clip['clip_number']}")

        # Get progress
        progress = db.get_video_progress(video['id'])
        print(f"Progress: {progress}")
    else:
        print("No active video found")


if __name__ == "__main__":
    print("AI Content Creator - Example Usage")
    print("=" * 60)

    # Uncomment the functions you want to test

    # example_add_video()
    # example_generate_clip()
    # example_generate_thumbnail()
    # example_generate_caption()
    # example_upload_to_facebook()
    # example_database_queries()

    print("\n" + "=" * 60)
    print("Examples complete!")
