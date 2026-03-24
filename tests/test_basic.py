"""
Unit tests for AI Content Creator
Run with: pytest tests/
"""
import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.caption_generator import CaptionGenerator
from src.database import Database


class TestCaptionGenerator(unittest.TestCase):
    def setUp(self):
        self.caption_gen = CaptionGenerator()

    def test_simple_caption(self):
        caption = self.caption_gen.generate_caption(
            clip_number=1,
            total_clips=10,
            style='simple'
        )
        self.assertIn("Part 1 of 10", caption)

    def test_engaging_caption(self):
        caption = self.caption_gen.generate_caption(
            clip_number=1,
            total_clips=10,
            style='engaging'
        )
        self.assertIn("#", caption)  # Should have hashtags
        self.assertTrue(len(caption) > 20)

    def test_custom_caption(self):
        caption = self.caption_gen.generate_custom_caption(
            "Test {part}",
            part=5
        )
        self.assertEqual(caption, "Test 5")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use test database
        self.db = Database(Path("test.db"))

    def tearDown(self):
        # Clean up test database
        if Path("test.db").exists():
            Path("test.db").unlink()

    def test_add_video(self):
        video_id = self.db.add_video(
            "test.mp4",
            "/path/to/test.mp4",
            600,  # 10 minutes
            5     # 5 min clips
        )
        self.assertIsNotNone(video_id)
        self.assertGreater(video_id, 0)

    def test_get_active_video(self):
        # Add video first
        self.db.add_video("test.mp4", "/path/test.mp4", 600, 5)

        # Get active video
        video = self.db.get_active_video()
        self.assertIsNotNone(video)
        self.assertEqual(video['file_name'], "test.mp4")


if __name__ == '__main__':
    unittest.main()
