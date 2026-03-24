"""
Facebook uploader using Graph API
"""
import requests
import time
from pathlib import Path
from typing import Optional, Dict

from config.settings import (
    FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID,
    FACEBOOK_API_BASE_URL, MAX_RETRIES, RETRY_DELAY
)
from src.logger import logger


class FacebookUploader:
    def __init__(self):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.api_base_url = FACEBOOK_API_BASE_URL

    def validate_credentials(self) -> bool:
        """Validate Facebook access token and page ID"""
        if not self.access_token or not self.page_id:
            logger.error("Facebook credentials not configured!")
            logger.error("Please set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env file")
            return False

        try:
            # Test API call to verify token
            url = f"{self.api_base_url}/me"
            params = {'access_token': self.access_token}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.success(f"Facebook credentials validated for: {data.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"Invalid credentials: {response.json()}")
                return False

        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
            return False

    def upload_video(self, video_path: str, caption: str,
                    thumbnail_path: Optional[str] = None) -> Optional[str]:
        """
        Upload video to Facebook Page

        Args:
            video_path: Path to video file
            caption: Video caption/description
            thumbnail_path: Optional thumbnail path

        Returns:
            Facebook post ID if successful, None otherwise
        """
        video_file = Path(video_path)

        if not video_file.exists():
            logger.error(f"Video file not found: {video_path}")
            return None

        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        logger.info(f"Uploading video: {video_file.name} ({file_size_mb:.2f} MB)")

        # Try upload with retries
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                post_id = self._upload_with_resumable(
                    video_path, caption, thumbnail_path
                )

                if post_id:
                    logger.success(f"Video uploaded successfully! Post ID: {post_id}")
                    return post_id

            except Exception as e:
                logger.error(f"Upload attempt {attempt} failed: {str(e)}")

                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Upload failed.")

        return None

    def _upload_with_resumable(self, video_path: str, caption: str,
                               thumbnail_path: Optional[str] = None) -> Optional[str]:
        """
        Upload video using resumable upload (for larger files)

        This is a 3-step process:
        1. Initialize upload session
        2. Upload video file
        3. Publish video with caption
        """

        # Step 1: Initialize upload session
        logger.info("Step 1: Initializing upload session...")
        upload_url = f"{self.api_base_url}/{self.page_id}/videos"

        file_size = Path(video_path).stat().st_size

        init_params = {
            'access_token': self.access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }

        response = requests.post(upload_url, data=init_params)

        if response.status_code != 200:
            logger.error(f"Failed to initialize upload: {response.json()}")
            return None

        upload_session_id = response.json().get('upload_session_id')
        video_id = response.json().get('video_id')

        logger.info(f"Upload session initialized: {upload_session_id}")

        # Step 2: Upload video file
        logger.info("Step 2: Uploading video file...")

        with open(video_path, 'rb') as video_file:
            upload_params = {
                'access_token': self.access_token,
                'upload_phase': 'transfer',
                'upload_session_id': upload_session_id,
            }

            files = {'video_file_chunk': video_file}

            response = requests.post(upload_url, data=upload_params, files=files)

            if response.status_code != 200:
                logger.error(f"Failed to upload video: {response.json()}")
                return None

        logger.info("Video file uploaded successfully")

        # Step 3: Finalize and publish
        logger.info("Step 3: Publishing video...")

        publish_params = {
            'access_token': self.access_token,
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            'description': caption,
        }

        # Add thumbnail if provided
        if thumbnail_path and Path(thumbnail_path).exists():
            with open(thumbnail_path, 'rb') as thumb_file:
                files = {'thumb': thumb_file}
                response = requests.post(upload_url, data=publish_params, files=files)
        else:
            response = requests.post(upload_url, data=publish_params)

        if response.status_code != 200:
            logger.error(f"Failed to publish video: {response.json()}")
            return None

        result = response.json()
        post_id = result.get('id') or video_id

        return post_id

    def _upload_simple(self, video_path: str, caption: str) -> Optional[str]:
        """
        Simple upload method (for smaller videos < 1GB)

        Args:
            video_path: Path to video file
            caption: Video caption

        Returns:
            Post ID if successful
        """
        url = f"{self.api_base_url}/{self.page_id}/videos"

        with open(video_path, 'rb') as video_file:
            files = {'source': video_file}
            data = {
                'access_token': self.access_token,
                'description': caption,
            }

            response = requests.post(url, data=data, files=files)

            if response.status_code == 200:
                post_id = response.json().get('id')
                return post_id
            else:
                logger.error(f"Upload failed: {response.json()}")
                return None

    def get_video_status(self, video_id: str) -> Dict:
        """
        Check video upload status

        Args:
            video_id: Facebook video ID

        Returns:
            Video status information
        """
        try:
            url = f"{self.api_base_url}/{video_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'status,description,created_time'
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get video status: {response.json()}")
                return {}

        except Exception as e:
            logger.error(f"Error getting video status: {str(e)}")
            return {}

    def delete_video(self, video_id: str) -> bool:
        """
        Delete video from Facebook

        Args:
            video_id: Facebook video ID

        Returns:
            True if successful
        """
        try:
            url = f"{self.api_base_url}/{video_id}"
            params = {'access_token': self.access_token}

            response = requests.delete(url, params=params)

            if response.status_code == 200:
                logger.success(f"Video {video_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete video: {response.json()}")
                return False

        except Exception as e:
            logger.error(f"Error deleting video: {str(e)}")
            return False

    def get_page_info(self) -> Dict:
        """Get Facebook page information"""
        try:
            url = f"{self.api_base_url}/{self.page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'name,fan_count,category'
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting page info: {str(e)}")
            return {}

    def test_connection(self) -> bool:
        """Test Facebook API connection"""
        logger.info("Testing Facebook API connection...")

        if not self.validate_credentials():
            return False

        page_info = self.get_page_info()
        if page_info:
            logger.success(f"Connected to page: {page_info.get('name', 'Unknown')}")
            logger.info(f"Fans: {page_info.get('fan_count', 0)}")
            return True

        return False
