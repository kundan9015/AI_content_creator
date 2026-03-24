"""
Database handler using SQLite for progress tracking
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config.settings import DATABASE_PATH


class Database:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                clip_duration INTEGER NOT NULL,
                total_clips INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                completed_at TIMESTAMP NULL
            )
        """)

        # Clips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                clip_number INTEGER NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                clip_path TEXT,
                thumbnail_path TEXT,
                caption TEXT,
                status TEXT DEFAULT 'pending',
                facebook_post_id TEXT,
                uploaded_at TIMESTAMP NULL,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        """)

        # Upload schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                scheduled_time TEXT NOT NULL,
                last_run TIMESTAMP NULL,
                next_run TIMESTAMP NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        """)

        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_video(self, file_name: str, file_path: str, duration_seconds: int,
                  clip_duration: int) -> int:
        """Add new video to database"""
        total_clips = (duration_seconds // (clip_duration * 60)) + 1

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO videos (file_name, file_path, duration_seconds,
                              clip_duration, total_clips)
            VALUES (?, ?, ?, ?, ?)
        """, (file_name, file_path, duration_seconds, clip_duration, total_clips))

        video_id = cursor.lastrowid

        # Create clip entries
        for i in range(total_clips):
            start_time = i * clip_duration * 60
            end_time = min((i + 1) * clip_duration * 60, duration_seconds)

            cursor.execute("""
                INSERT INTO clips (video_id, clip_number, start_time, end_time)
                VALUES (?, ?, ?, ?)
            """, (video_id, i + 1, start_time, end_time))

        conn.commit()
        conn.close()

        return video_id

    def get_active_video(self) -> Optional[Dict]:
        """Get currently active video"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM videos
            WHERE status = 'active'
            ORDER BY added_at ASC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_next_pending_clip(self, video_id: int) -> Optional[Dict]:
        """Get next pending clip for upload"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM clips
            WHERE video_id = ? AND status = 'pending'
            ORDER BY clip_number ASC
            LIMIT 1
        """, (video_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def update_clip_status(self, clip_id: int, status: str,
                          facebook_post_id: Optional[str] = None,
                          error_message: Optional[str] = None):
        """Update clip status after upload attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status == 'uploaded':
            cursor.execute("""
                UPDATE clips
                SET status = ?, facebook_post_id = ?, uploaded_at = ?,
                    error_message = NULL
                WHERE id = ?
            """, (status, facebook_post_id, datetime.now(), clip_id))
        else:
            cursor.execute("""
                UPDATE clips
                SET status = ?, error_message = ?, retry_count = retry_count + 1
                WHERE id = ?
            """, (status, error_message, clip_id))

        conn.commit()
        conn.close()

    def update_clip_paths(self, clip_id: int, clip_path: str,
                         thumbnail_path: str, caption: str):
        """Update clip file paths and caption"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE clips
            SET clip_path = ?, thumbnail_path = ?, caption = ?
            WHERE id = ?
        """, (clip_path, thumbnail_path, caption, clip_id))

        conn.commit()
        conn.close()

    def get_video_progress(self, video_id: int) -> Dict:
        """Get upload progress for a video"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_clips,
                SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END) as uploaded,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM clips
            WHERE video_id = ?
        """, (video_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else {}

    def mark_video_complete(self, video_id: int):
        """Mark video as complete when all clips uploaded"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE videos
            SET status = 'completed', completed_at = ?
            WHERE id = ?
        """, (datetime.now(), video_id))

        conn.commit()
        conn.close()

    def add_log(self, action: str, status: str, message: str, details: str = ""):
        """Add activity log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO activity_logs (action, status, message, details)
            VALUES (?, ?, ?, ?)
        """, (action, status, message, details))

        conn.commit()
        conn.close()

    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent activity logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM activity_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_videos(self) -> List[Dict]:
        """Get all videos with their progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT v.*,
                   COUNT(c.id) as total_clips,
                   SUM(CASE WHEN c.status = 'uploaded' THEN 1 ELSE 0 END) as uploaded_clips
            FROM videos v
            LEFT JOIN clips c ON v.id = c.video_id
            GROUP BY v.id
            ORDER BY v.added_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
