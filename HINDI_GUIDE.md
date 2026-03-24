# 🎬 AI CONTENT CREATOR - KAISE CHALAYE (Hindi Guide)

---

## ⚡ SABSE PEHLE YE KARO (One-Time Setup)

### 1️⃣ START.bat Run Karo (Automatic Setup)

```bash
# Double-click karo is file pe:
START.bat
```

**Ye automatically:**
- Python check karega
- Dependencies install karega
- .env file banega
- Project initialize hoga

**Time:** 2-3 minutes

---

### 2️⃣ Facebook Token Configure Karo

`START.bat` ke baad Notepad khulega `.env` file ke sath.

**Edit karo ye 2 lines:**

```
FACEBOOK_ACCESS_TOKEN=your_actual_token_here
FACEBOOK_PAGE_ID=your_actual_page_id_here
```

**Token kaise milega? Niche dekho! ⬇️**

---

## 🔑 FACEBOOK TOKEN KAISE MILEGA (2 minutes)

### Step 1: Developers Site Pe Jao
```
https://developers.facebook.com/tools/explorer/
```

### Step 2: Generate Token
1. **Graph API Explorer** kholo
2. **"Generate Access Token"** button click karo
3. **Permissions** select karo:
   - ✅ pages_manage_posts
   - ✅ pages_read_engagement
   - ✅ pages_show_list
4. **Token dikha?** Copy karo! ✅

### Step 3: Page ID Nikalo
1. Graph API Explorer mein hi raho
2. Query box mein type karo: `/me/accounts`
3. **Submit** click karo
4. Tumhare page ka **ID** dikha? Copy karo! ✅

### Step 4: .env Mein Dalo
```
notepad .env
```

Token aur Page ID paste karo, save karo!

**Done! Facebook setup complete! ✅**

---

## 🎬 VIDEO UPLOAD KAISE KARE (Step-by-Step)

### STEP 1: Video Copy Karo

```bash
# Apni movie/video ko copy karo
copy "C:\Movies\movie.mp4" data\videos\
```

### STEP 2: Video Add Karo Database Mein

```bash
python main.py --add-video data/videos/movie.mp4
```

**Dikha kuch aisa:**
```
✓ Video added successfully!
  Duration: 180 minutes
  Total clips: 18
  Clip duration: 10 minutes
```

### STEP 3: Facebook Connection Test Karo

```bash
python main.py --test-facebook
```

**Agar sahi hai to:**
```
✓ Facebook connection successful!
✓ Connected to page: Your Page Name
```

**Agar error aaye:**
- `.env` file check karo
- Token sahi hai?
- Page ID sahi hai?

### STEP 4: First Clip Upload Karo!

```bash
python main.py --upload-now
```

**Kya hoga:**
1. Video ka pehla 10-min clip generate hoga
2. Thumbnail banega
3. Caption likha jayega
4. Facebook pe upload hoga

**Time lagega:** 2-4 minutes

**Output:**
```
✓ Clip generated: clip_001.mp4
✓ Thumbnail generated
✓ Video uploaded successfully!
  Post ID: 123456789
```

**DONE! Pehla clip upload ho gaya! 🎉**

### STEP 5: Status Check Karo

```bash
python main.py --status
```

**Output:**
```
📹 Video: movie.mp4
   Uploaded: 1/18
   Pending: 17
   Next clip: 2
```

---

## ⏰ AUTOMATIC DAILY UPLOAD KAISE SETUP KARE

### Option A: Simple Python Scheduler

```bash
python main.py --start-scheduler
```

**Note:**
- Terminal window khuli rehni chahiye
- PC on hona chahiye 9 AM pe
- Ctrl+C se band hoga

### Option B: Windows Task Scheduler (BEST!) ⭐

Ye ek baar setup karo, phir tension free! 🚀

**Steps:**

1. **Windows Search** mein type karo: `Task Scheduler`
2. **"Create Basic Task"** click karo
3. **Name:** `AI Content Creator`
4. **Trigger:** Daily
5. **Time:** 09:00 AM (ya jo tumhe chahiye)
6. **Action:** Start a program
7. **Program:**
   ```
   python
   ```
8. **Arguments:**
   ```
   main.py --upload-now
   ```
9. **Start in:**
   ```
   D:\AI_content_creator
   ```
   *(apna actual path dalo)*
10. **Finish** click karo

**DONE! Ab har roz 9 AM pe automatic upload! 🎯**

---

## 📊 DAILY KAISE CHALEGA (Example)

```
🗓️ Day 1 (Manual - tumne):
   9:30 AM → python main.py --upload-now
           → Clip 1 (0-10 min) uploaded ✅

🗓️ Day 2 (Automatic):
   9:00 AM → Task Scheduler automatically runs
           → Clip 2 (10-20 min) uploaded ✅

🗓️ Day 3 (Automatic):
   9:00 AM → Clip 3 (20-30 min) uploaded ✅

...continues daily...

🗓️ Day 18 (Automatic):
   9:00 AM → Clip 18 (170-180 min) uploaded ✅
           → System: "All clips uploaded! 🎉"
```

**Total: 18 days mein puri movie Facebook pe! 🎬**

---

## 🛠️ USEFUL COMMANDS

### Status Check Karna
```bash
python main.py --status
```
Batata hai kitne clips upload hue, kitne pending hain.

### Next Clip Preview
```bash
python main.py --preview
```
Next clip kya hogi, uska preview dikhata hai.

### Manual Upload
```bash
python main.py --upload-now
```
Abhi upload kar do, wait mat karo.

### Facebook Test
```bash
python main.py --test-facebook
```
Check karo Facebook connection sahi hai ya nahi.

### Help
```bash
python main.py --help
```
Sare commands dikhata hai.

---

## ⚠️ COMMON PROBLEMS & SOLUTIONS

### Problem 1: "FFmpeg not found"

**Solution (Windows):**
```bash
# Chocolatey se install karo (agar hai)
choco install ffmpeg

# Ya manual download:
# https://ffmpeg.org/download.html
# Extract karo aur PATH mein add karo
```

**Test karo:**
```bash
ffmpeg -version
```

### Problem 2: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem 3: "Facebook error"

**Solution:**
```bash
# .env file check karo
notepad .env

# Token sahi hai?
# Page ID sahi hai?
# Token expired to nahi?

# Test karo
python main.py --test-facebook
```

### Problem 4: "Video file not found"

**Solution:**
```bash
# Video path check karo
dir data\videos\

# Video file hai waha?
# Path sahi diya tumne?
```

### Problem 5: Upload slow hai

**Normal hai!** Video processing time lagta hai:
- Clip generation: 30-60 seconds
- Upload: 1-2 minutes
- **Total:** 2-4 minutes per clip

---

## 📁 IMPORTANT FILES & FOLDERS

```
AI_content_creator/
├── data/
│   ├── videos/          ← Apni video yaha dalo
│   ├── clips/           ← Generated clips yaha aati hain
│   ├── thumbnails/      ← Thumbnails yaha banti hain
│   └── database.db      ← Progress yaha save hota hai
│
├── logs/                ← Log files yaha hain
│   └── app_20260324.log
│
├── .env                 ← Configuration file (TOKEN yaha!)
├── main.py              ← Main program
└── START.bat            ← Quick setup script
```

---

## 💡 PRO TIPS

1. **🎬 Testing:** Pehle choti video se test karo (5-10 min ki)
2. **📊 Monitor:** First 2-3 uploads khud dekho, check karo sab theek hai
3. **⏰ Schedule:** Best time choose karo when PC on hota hai
4. **📝 Logs:** Agar problem ho to `logs/` folder check karo
5. **🔑 Token:** 60 days mein expire hota hai, reminder laga lo
6. **💾 Backup:** `database.db` ka backup rakho
7. **📱 Notification:** Email/Telegram notification setup karo (optional)

---

## 📞 HELP CHAHIYE?

### Detailed Documentation
```bash
notepad README.md
```
Complete guide with screenshots

### Verify Setup
```bash
python verify_setup.py
```
Automatically check karta hai sab kuch sahi hai ya nahi

### Check Logs
```bash
notepad logs/app_20260324.log
```
Dekhne ke liye kya ho raha hai

---

## 🎯 COMPLETE WORKFLOW (Copy-Paste)

Naye project ke liye ye commands ek-ek karke run karo:

```bash
# 1. Setup (one time)
START.bat

# 2. Edit .env (notepad khulega)
# Add: FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID

# 3. Video copy karo
copy "C:\path\to\movie.mp4" data\videos\

# 4. Video add karo
python main.py --add-video data/videos/movie.mp4

# 5. Test karo
python main.py --test-facebook

# 6. First upload
python main.py --upload-now

# 7. Status dekho
python main.py --status

# 8. Windows Task Scheduler setup karo (manual)
# Ab daily automatic upload hoga!
```

---

## 🎉 SUCCESS CHECKLIST

Ye sab check karo:

- ✅ Python 3.8+ installed hai
- ✅ FFmpeg installed hai
- ✅ Dependencies installed hain (`pip list`)
- ✅ `.env` file configured hai
- ✅ Video data/videos/ mein hai
- ✅ Database mein video add ho gaya
- ✅ Facebook connection successful hai
- ✅ First clip upload ho gaya
- ✅ Task Scheduler setup ho gaya

**Sab ✅? CONGRATULATIONS! Tum ready ho! 🚀**

---

## 🔥 FINAL CHECKLIST (Before Starting)

1. **Python hai?** → `python --version`
2. **FFmpeg hai?** → `ffmpeg -version`
3. **Dependencies installed?** → `pip list`
4. **.env configured?** → `notepad .env`
5. **Video ready hai?** → `dir data\videos`
6. **Facebook token ready?** → Test karo

**Sab ready? AB SHURU KARO! 🎬**

---

## 💬 NOTES

- **PC on rakho** upload time pe
- **Internet on rakho**
- **Disk space** check karo (clips ke liye)
- **First 18 days** PC 9 AM pe on rakho (automatic upload)
- **Token renew** karo 60 days baad

---

**HAPPY CONTENT CREATING! 🎉📹✨**

**Questions? README.md padho ya logs check karo!**

---

*Made with ❤️ for Hindi-speaking content creators*
