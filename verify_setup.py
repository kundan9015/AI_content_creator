"""
Installation verification and setup helper
Run this after installation to verify everything is configured correctly
"""
import sys
from pathlib import Path
import subprocess


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} found, but 3.8+ required")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ {version_line}")
            return True
    except FileNotFoundError:
        print("✗ FFmpeg not found")
        print("  Install: https://ffmpeg.org/download.html")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking Python packages...")
    required = [
        'moviepy',
        'PIL',  # Pillow
        'requests',
        'dotenv',
        'schedule'
    ]

    all_ok = True
    for package in required:
        try:
            if package == 'PIL':
                __import__('PIL')
                print(f"✓ Pillow installed")
            elif package == 'dotenv':
                __import__('dotenv')
                print(f"✓ python-dotenv installed")
            else:
                __import__(package)
                print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            all_ok = False

    if not all_ok:
        print("\nInstall missing packages:")
        print("  pip install -r requirements.txt")

    return all_ok


def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    dirs = [
        'config',
        'src',
        'data/videos',
        'data/clips',
        'data/thumbnails',
        'logs'
    ]

    all_ok = True
    for dir_path in dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/ exists")
        else:
            print(f"✗ {dir_path}/ missing")
            all_ok = False

    return all_ok


def check_config():
    """Check if .env file exists"""
    print("\nChecking configuration...")

    if Path('.env').exists():
        print("✓ .env file exists")

        # Check if configured
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_facebook_access_token_here' in content:
                print("⚠ .env file not configured yet")
                print("  Edit .env and add your Facebook credentials")
                return False
            else:
                print("✓ .env appears configured")
                return True
    else:
        print("✗ .env file not found")
        print("  Copy .env.example to .env:")
        print("  cp .env.example .env")
        return False


def test_imports():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")

    modules = [
        'config.settings',
        'src.database',
        'src.video_processor',
        'src.thumbnail_generator',
        'src.caption_generator',
        'src.uploader',
        'src.scheduler',
        'src.notifier',
        'src.logger'
    ]

    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} OK")
        except Exception as e:
            print(f"✗ {module} failed: {str(e)}")
            all_ok = False

    return all_ok


def print_next_steps():
    """Print next steps for user"""
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Configure .env file:
   - Add FACEBOOK_ACCESS_TOKEN
   - Add FACEBOOK_PAGE_ID
   - Set VIDEO_PATH

2. Initialize project:
   python main.py --init

3. Add a video:
   python main.py --add-video data/videos/your_video.mp4

4. Test Facebook connection:
   python main.py --test-facebook

5. Upload first clip:
   python main.py --upload-now

6. Start scheduler:
   python main.py --start-scheduler

For help: python main.py --help
Full guide: See README.md
""")


def main():
    """Run all checks"""
    print("=" * 60)
    print("AI CONTENT CREATOR - INSTALLATION VERIFICATION")
    print("=" * 60)

    checks = {
        'Python version': check_python_version(),
        'FFmpeg': check_ffmpeg(),
        'Dependencies': check_dependencies(),
        'Directories': check_directories(),
        'Configuration': check_config(),
        'Module imports': test_imports()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, status in checks.items():
        icon = "✓" if status else "✗"
        print(f"{icon} {name}: {'OK' if status else 'FAILED'}")

    all_ok = all(checks.values())

    if all_ok:
        print("\n✓ All checks passed! System ready to use.")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")

    print_next_steps()


if __name__ == "__main__":
    main()
