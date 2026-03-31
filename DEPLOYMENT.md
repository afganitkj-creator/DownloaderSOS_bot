# 🚀 PANDUAN DEPLOYMENT BOT TELEGRAM 24/7

Bot Telegram Anda bisa dijalankan terus-menerus (24/7) di cloud tanpa biaya atau dengan biaya minimal.

## **OPSI 1: Railway.app (PALING MUDAH - GRATIS) ⭐**

### Langkah 1: Persiapan di GitHub
Bot Anda sudah ada di GitHub, tinggal connect ke Railway.

### Langkah 2: Connect ke Railway
1. Buka [railway.app](https://railway.app)
2. Login dengan GitHub
3. Klik "New Project" → "Deploy from GitHub Repo"
4. Pilih repository `DownloaderSOS_bot`
5. Railway akan otomatis detect `Dockerfile`

### Langkah 3: Setup Environment Variables
Di Railway Dashboard:
1. Buka project → Variables
2. Tambahkan:
   ```
   BOT_TOKEN=8391302606:AAHJJ0noM8pJAmCAi1LrjY635lzXmM5zYVk
   ILOVEPDF_PUBLIC_KEY=your_key
   ILOVEPDF_SECRET_KEY=your_secret
   ```

### Langkah 4: Deploy
- Railway otomatis deploy saat ada `git push`
- Bot langsung jalan 24/7! ✅

---

## **OPSI 2: Render.com (GRATIS, KURANG CANGGIH)**

### Langkah 1: Create Service
1. Buka [render.com](https://render.com)
2. Login dengan GitHub
3. "New+" → "Web Service"
4. Connect GitHub repository

### Langkah 2: Configure
- **Name**: `downloader-sos-bot`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Plan**: Free (bisa naik upgrade kemudian)

### Langkah 3: Environment Variables
Add di "Environment":
```
BOT_TOKEN=your_token
ILOVEPDF_PUBLIC_KEY=your_key
ILOVEPDF_SECRET_KEY=your_secret
```

### Langkah 4: Deploy
Klik "Create Web Service" - Deploy otomatis! ✅

---

## **OPSI 3: Docker Compose (Lokal/VPS)**

Jika mau jalankan di server sendiri atau laptop:

### Jalankan dengan Docker:
```bash
# Build image
docker build -t downloader-sos-bot .

# Run container
docker run -d \
  -e BOT_TOKEN="your_token" \
  -e ILOVEPDF_PUBLIC_KEY="your_key" \
  -e ILOVEPDF_SECRET_KEY="your_secret" \
  --restart always \
  --name sos-bot \
  downloader-sos-bot
```

### Cek status bot:
```bash
docker logs -f sos-bot
```

---

## **OPSI 4: GitHub Actions (AUTO-DEPLOY) ⚡**

Setup automatic deployment dari GitHub:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm i -g @railway/cli
          railway deploy --offline
```

---

## ⚡ REKOMENDASI TERBAIK

| Platform | Harga | Setup | 24/7 | Rating |
|----------|-------|-------|------|--------|
| **Railway** | FREE | ⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| Render | FREE | ⭐⭐ | ~18h/day | ⭐⭐⭐ |
| Heroku | BAYAR | ⭐⭐ | ✅ | ⭐⭐⭐ |
| VPS | BAYAR | ⭐ | ✅ | ⭐⭐⭐⭐ |

---

## 📋 CHECKLIST SEBELUM DEPLOY

- [ ] BOT_TOKEN valid (sudah test sebelumnya ✅)
- [ ] ILOVEPDF keys siap (opsional, ada fallback local)
- [ ] Dockerfile sudah ada di repo ✅
- [ ] requirements.txt updated ✅
- [ ] bot.py siap tanpa error
- [ ] GitHub push terakhir done

---

## 🔧 CARA CEK BOT JALAN

Kirim message ke bot di Telegram → Bot harus respond!

---

## 📞 TROUBLESHOOTING

### Bot tidak respond
```bash
# Check logs di Railway/Render dashboard
# Atau di Docker:
docker logs sos-bot
```

### Crash karena memory
- Railway/Render: upgrade plan
- Docker: kurangi image quality di settings

### Token error
- Pastikan BOT_TOKEN benar di environment variables
- Jangan shared di public!

---

## 💡 TIPS TAMBAHAN

1. **Keep-Alive**: Platform cloud bisa sleep, tambahkan ping setiap jam
2. **Backup**: Jangan lupa backup database kalau ada user data
3. **Monitoring**: Setup alerts jika bot crash
4. **Update**: Setiap update bot tinggal `git push` - deploy otomatis!

---

**Siap deploy? Pilih satu opsi di atas dan mulai! 🚀**
