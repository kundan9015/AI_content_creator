"""
Caption generator for video clips
"""
import random
from datetime import datetime
from typing import Dict

from src.logger import logger


class CaptionGenerator:
    def __init__(self):
        self.templates = self._load_templates()
        self.hashtags = self._load_hashtags()

    def _load_templates(self) -> list:
        """Load caption templates"""
        return [
            "Part {part} of {total} 🎬",
            "Episode {part} | {total} Part Series 📺",
            "Watch Part {part}/{total} Now! 🔥",
            "Part {part} - Keep Watching! 👀",
            "Episode {part} is Here! Don't Miss It! ✨",
            "{part}/{total} - More Coming Soon! 🎥",
            "New Episode Alert! Part {part} 🚨",
            "Part {part} | Full Series Available 📹",
            "Enjoying the series? This is Part {part}! ❤️",
            "Part {part} of {total} - Comment Your Thoughts! 💭",
        ]

    def _load_hashtags(self) -> dict:
        """Load hashtag categories"""
        return {
            'general': [
                '#viral', '#trending', '#entertainment', '#video',
                '#watchnow', '#mustsee', '#content', '#creator'
            ],
            'movie': [
                '#movie', '#film', '#cinema', '#movieclips',
                '#movienight', '#films', '#movietime', '#movielovers'
            ],
            'series': [
                '#series', '#webseries', '#episode', '#binge',
                '#bingewatch', '#episodes', '#serialkillers', '#tvshow'
            ],
            'engagement': [
                '#followforfollowback', '#like4like', '#viral', '#explore',
                '#instagood', '#reels', '#foryou', '#fyp'
            ]
        }

    def generate_caption(self, clip_number: int, total_clips: int,
                        video_name: str = None, style: str = 'default') -> str:
        """
        Generate caption for a video clip

        Args:
            clip_number: Current clip number
            total_clips: Total number of clips
            video_name: Name of the video (optional)
            style: Caption style ('default', 'engaging', 'simple')

        Returns:
            Generated caption
        """
        try:
            if style == 'simple':
                caption = f"Part {clip_number} of {total_clips}"

            elif style == 'engaging':
                template = random.choice(self.templates)
                caption = template.format(part=clip_number, total=total_clips)

                # Add video name if provided
                if video_name:
                    caption = f"{video_name}\n{caption}"

                # Add call to action
                if clip_number < total_clips:
                    cta = random.choice([
                        "\n\n👉 Follow for the next part!",
                        "\n\n🔔 Stay tuned for more!",
                        "\n\n💫 More episodes coming!",
                        "\n\n⏭ Next part coming soon!",
                    ])
                    caption += cta

            else:  # default
                caption = f"Part {clip_number}/{total_clips}"
                if video_name:
                    caption = f"{video_name} - {caption}"

            # Add hashtags
            hashtags = self._generate_hashtags(style)
            caption = f"{caption}\n\n{hashtags}"

            logger.info(f"Generated caption for clip {clip_number}")
            return caption

        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            # Fallback to simple caption
            return f"Part {clip_number} of {total_clips}"

    def generate_custom_caption(self, template: str, **kwargs) -> str:
        """
        Generate caption from custom template

        Args:
            template: Caption template with placeholders
            **kwargs: Values for placeholders

        Returns:
            Generated caption

        Example:
            template = "Watch {title} - Part {part}"
            generate_custom_caption(template, title="My Video", part=1)
        """
        try:
            caption = template.format(**kwargs)
            logger.info("Generated custom caption")
            return caption
        except Exception as e:
            logger.error(f"Error with custom caption: {str(e)}")
            return template

    def _generate_hashtags(self, style: str = 'default') -> str:
        """Generate hashtags based on style"""
        tags = []

        if style == 'engaging':
            # Mix of all categories
            tags.extend(random.sample(self.hashtags['general'], 2))
            tags.extend(random.sample(self.hashtags['series'], 2))
            tags.extend(random.sample(self.hashtags['engagement'], 3))
        elif style == 'simple':
            # Just basic tags
            tags.extend(random.sample(self.hashtags['general'], 3))
        else:  # default
            tags.extend(random.sample(self.hashtags['general'], 2))
            tags.extend(random.sample(self.hashtags['series'], 2))

        return ' '.join(tags)

    def generate_caption_with_timing(self, clip_number: int, total_clips: int,
                                    start_time: str, end_time: str) -> str:
        """
        Generate caption with time information

        Args:
            clip_number: Current clip number
            total_clips: Total clips
            start_time: Start time (formatted)
            end_time: End time (formatted)

        Returns:
            Caption with timing info
        """
        caption = f"Part {clip_number}/{total_clips}\n"
        caption += f"⏰ {start_time} - {end_time}\n\n"

        if clip_number < total_clips:
            caption += "👉 Follow for more parts!\n\n"

        hashtags = self._generate_hashtags()
        caption += hashtags

        return caption

    def generate_series_description(self, video_name: str,
                                   total_clips: int,
                                   description: str = None) -> str:
        """
        Generate description for the entire series

        Args:
            video_name: Name of the video series
            total_clips: Total number of clips
            description: Optional description

        Returns:
            Series description
        """
        desc = f"📺 {video_name}\n\n"

        if description:
            desc += f"{description}\n\n"

        desc += f"🎬 Total Episodes: {total_clips}\n"
        desc += f"📅 New episodes daily\n\n"
        desc += "Follow us for all episodes! 🔔\n\n"

        hashtags = ' '.join(
            self.hashtags['general'][:3] +
            self.hashtags['series'][:3]
        )
        desc += hashtags

        return desc

    def add_custom_hashtags(self, caption: str, custom_tags: list) -> str:
        """Add custom hashtags to caption"""
        formatted_tags = [f"#{tag.strip('#')}" for tag in custom_tags]
        return f"{caption}\n\n{' '.join(formatted_tags)}"

    def get_caption_stats(self, caption: str) -> Dict:
        """Get statistics about a caption"""
        return {
            'length': len(caption),
            'word_count': len(caption.split()),
            'hashtag_count': caption.count('#'),
            'emoji_count': sum(1 for c in caption if ord(c) > 127000),
            'newlines': caption.count('\n')
        }
