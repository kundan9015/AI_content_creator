"""
Cloud Dashboard - Lightweight Flask App for Render.com
Handles web interface, video uploads, and PC communication
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime
import secrets
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max upload

# Configuration
UPLOAD_FOLDER = Path('temp_uploads')
DB_PATH = Path('cloud_dashboard.db')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

UPLOAD_FOLDER.mkdir(exist_ok=True)


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database"""
    conn = get_db()
    cursor = conn.cursor()

    # PC agents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pc_id TEXT UNIQUE NOT NULL,
            pc_name TEXT,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'offline',
            current_video TEXT,
            progress INTEGER DEFAULT 0,
            total_clips INTEGER DEFAULT 0,
            uploaded_clips INTEGER DEFAULT 0
        )
    """)

    # Commands queue
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pc_id TEXT NOT NULL,
            command TEXT NOT NULL,
            data TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_at TIMESTAMP
        )
    """)

    # Settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pc_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pc_id, key)
        )
    """)

    # Upload queue
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upload_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pc_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            filesize INTEGER,
            clip_duration INTEGER DEFAULT 10,
            status TEXT DEFAULT 'pending',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            downloaded_at TIMESTAMP
        )
    """)

    # Activity logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pc_id TEXT,
            action TEXT NOT NULL,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_log(pc_id, action, message):
    """Add activity log"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_logs (pc_id, action, message)
        VALUES (?, ?, ?)
    """, (pc_id, action, message))
    conn.commit()
    conn.close()


# ============================================================
# WEB ROUTES
# ============================================================

@app.route('/')
def index():
    """Dashboard home page"""
    conn = get_db()
    cursor = conn.cursor()

    # Get all agents
    cursor.execute("SELECT * FROM agents ORDER BY last_seen DESC")
    agents = [dict(row) for row in cursor.fetchall()]

    # Get recent logs
    cursor.execute("""
        SELECT * FROM activity_logs
        ORDER BY timestamp DESC LIMIT 20
    """)
    logs = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('index.html', agents=agents, logs=logs)


@app.route('/upload')
def upload_page():
    """Video upload page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pc_id, pc_name, status FROM agents WHERE status='online'")
    agents = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('upload.html', agents=agents)


@app.route('/settings')
def settings_page():
    """Settings page"""
    conn = get_db()
    cursor = conn.cursor()

    # Get agents
    cursor.execute("SELECT * FROM agents")
    agents = [dict(row) for row in cursor.fetchall()]

    # Get settings for each agent
    for agent in agents:
        cursor.execute("""
            SELECT key, value FROM settings
            WHERE pc_id = ?
        """, (agent['pc_id'],))
        agent['settings'] = {row['key']: row['value'] for row in cursor.fetchall()}

    conn.close()

    return render_template('settings.html', agents=agents)


@app.route('/history')
def history_page():
    """Upload history page"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM activity_logs
        WHERE action IN ('upload_complete', 'video_added')
        ORDER BY timestamp DESC LIMIT 100
    """)
    history = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('history.html', history=history)


# ============================================================
# API ENDPOINTS (PC Agent Communication)
# ============================================================

@app.route('/api/register', methods=['POST'])
def register_agent():
    """Register PC agent"""
    data = request.json
    pc_id = data.get('pc_id')
    pc_name = data.get('pc_name', 'Unknown PC')

    if not pc_id:
        return jsonify({'error': 'pc_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO agents (pc_id, pc_name, last_seen, status)
        VALUES (?, ?, ?, 'online')
    """, (pc_id, pc_name, datetime.now()))

    conn.commit()
    conn.close()

    add_log(pc_id, 'register', f'PC {pc_name} registered')

    return jsonify({'success': True, 'pc_id': pc_id})


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """PC agent heartbeat - updates status"""
    data = request.json
    pc_id = data.get('pc_id')

    if not pc_id:
        return jsonify({'error': 'pc_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Update agent status
    cursor.execute("""
        UPDATE agents SET
            last_seen = ?,
            status = 'online',
            current_video = ?,
            progress = ?,
            total_clips = ?,
            uploaded_clips = ?
        WHERE pc_id = ?
    """, (
        datetime.now(),
        data.get('current_video'),
        data.get('progress', 0),
        data.get('total_clips', 0),
        data.get('uploaded_clips', 0),
        pc_id
    ))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/commands/<pc_id>', methods=['GET'])
def get_commands(pc_id):
    """Get pending commands for PC"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM commands
        WHERE pc_id = ? AND status = 'pending'
        ORDER BY created_at ASC
    """, (pc_id,))

    commands = [dict(row) for row in cursor.fetchall()]

    # Mark as sent
    for cmd in commands:
        cursor.execute("""
            UPDATE commands SET status = 'sent'
            WHERE id = ?
        """, (cmd['id'],))

    conn.commit()
    conn.close()

    return jsonify({'commands': commands})


@app.route('/api/command-result', methods=['POST'])
def command_result():
    """PC reports command execution result"""
    data = request.json
    command_id = data.get('command_id')
    success = data.get('success', False)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE commands SET
            status = ?,
            executed_at = ?
        WHERE id = ?
    """, ('completed' if success else 'failed', datetime.now(), command_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    """Upload video file (temporary storage)"""
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['video']
    pc_id = request.form.get('pc_id')
    clip_duration = int(request.form.get('clip_duration', 10))

    if not pc_id:
        return jsonify({'error': 'pc_id required'}), 400

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Save file
    filename = secure_filename(file.filename)
    filepath = UPLOAD_FOLDER / f"{pc_id}_{filename}"
    file.save(str(filepath))

    filesize = filepath.stat().st_size

    # Add to queue
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO upload_queue (pc_id, filename, filesize, clip_duration)
        VALUES (?, ?, ?, ?)
    """, (pc_id, filename, filesize, clip_duration))

    queue_id = cursor.lastrowid

    # Create command for PC to download
    cursor.execute("""
        INSERT INTO commands (pc_id, command, data)
        VALUES (?, 'download_video', ?)
    """, (pc_id, json.dumps({
        'queue_id': queue_id,
        'filename': filename,
        'clip_duration': clip_duration
    })))

    conn.commit()
    conn.close()

    add_log(pc_id, 'video_uploaded', f'Video {filename} uploaded to cloud')

    return jsonify({
        'success': True,
        'queue_id': queue_id,
        'message': 'Video uploaded. PC will download it shortly.'
    })


@app.route('/api/download-video/<int:queue_id>', methods=['GET'])
def download_video(queue_id):
    """PC downloads video from cloud"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM upload_queue WHERE id = ?
    """, (queue_id,))

    item = cursor.fetchone()
    if not item:
        return jsonify({'error': 'Not found'}), 404

    item = dict(item)
    filepath = UPLOAD_FOLDER / f"{item['pc_id']}_{item['filename']}"

    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404

    # Mark as downloaded
    cursor.execute("""
        UPDATE upload_queue SET
            status = 'downloaded',
            downloaded_at = ?
        WHERE id = ?
    """, (datetime.now(), queue_id))

    conn.commit()
    conn.close()

    return send_file(str(filepath), as_attachment=True, download_name=item['filename'])


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings from web interface"""
    data = request.json
    pc_id = data.get('pc_id')
    settings = data.get('settings', {})

    if not pc_id:
        return jsonify({'error': 'pc_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    for key, value in settings.items():
        cursor.execute("""
            INSERT OR REPLACE INTO settings (pc_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        """, (pc_id, key, value, datetime.now()))

    # Notify PC agent about settings change
    cursor.execute("""
        INSERT INTO commands (pc_id, command, data)
        VALUES (?, 'update_settings', ?)
    """, (pc_id, json.dumps(settings)))

    conn.commit()
    conn.close()

    add_log(pc_id, 'settings_updated', 'Settings updated via dashboard')

    return jsonify({'success': True})


# ============================================================
# UTILITY ROUTES
# ============================================================

@app.route('/api/cleanup-temp', methods=['POST'])
def cleanup_temp():
    """Cleanup downloaded files from cloud"""
    queue_id = request.json.get('queue_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM upload_queue WHERE id = ?", (queue_id,))
    item = cursor.fetchone()

    if item:
        item = dict(item)
        filepath = UPLOAD_FOLDER / f"{item['pc_id']}_{item['filename']}"

        if filepath.exists():
            filepath.unlink()

        cursor.execute("UPDATE upload_queue SET status = 'processed' WHERE id = ?", (queue_id,))
        conn.commit()

    conn.close()

    return jsonify({'success': True})


@app.route('/health')
def health():
    """Health check endpoint for Render.com"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================
# INITIALIZE & RUN
# ============================================================

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
