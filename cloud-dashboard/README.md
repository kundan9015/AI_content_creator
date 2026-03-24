# 🎬 AI Content Creator - Cloud Dashboard

Web dashboard for controlling your AI Content Creator system from anywhere.

## 🚀 Deploy to Railway.app

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Quick Deploy

1. Click "Deploy on Railway" button above
2. Connect your GitHub account
3. Select this repository
4. Deploy!
5. Copy your URL: `https://your-project.up.railway.app`

### Manual Deploy

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

## 📁 Files

- `app.py` - Flask web server
- `templates/` - HTML templates
- `requirements.txt` - Python dependencies
- `railway.json` - Railway config
- `nixpacks.toml` - Build config
- `Procfile` - Process config

## ⚙️ Environment Variables

Set these in Railway Dashboard → Variables:

- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `PORT` - Auto-set by Railway

## 📊 Features

- Upload videos from anywhere
- Real-time progress monitoring
- Configure settings remotely
- View upload history
- Mobile-responsive design

## 🔗 Local Setup

After deploying, setup local PC agent:

```bash
cd ..
setup_agent.bat https://your-project.up.railway.app
```

## 📖 Documentation

See parent folder for complete guides:
- `RAILWAY_DEPLOYMENT.md` - Full Railway guide
- `README_HYBRID.md` - Architecture guide

## 🐛 Troubleshooting

**App not starting?**
- Check Railway logs
- Verify requirements.txt
- Ensure Python 3.10

**Database issues?**
- Add a Railway Volume
- Mount at `/app/data`

## 💰 Cost

FREE with Railway's $5/month credit!

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: discord.gg/railway
- Project Issues: Use GitHub Issues

---

Made with ❤️ for content creators
