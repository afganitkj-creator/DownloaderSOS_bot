# ⚡ QUICK START: Deploy di Railway (5 Menit)

Panduan tercepat untuk menjalankan bot 24/7 di Railway.app **GRATIS**.

## Step 1: Setup Railway Account
1. Buka https://railway.app
2. Klik **"Sign Up"**
3. Pilih **"Continue with GitHub"**
4. Authorize Railway untuk akses GitHub

## Step 2: Connect Repository
1. Di Railway dashboard, klik **"New Project"**
2. Pilih **"Deploy from GitHub Repo"**
3. Cari dan pilih repository **`DownloaderSOS_bot`**
4. Klik **"Deploy Now"**

Railway akan otomatis:
- ✅ Detect Dockerfile
- ✅ Build image
- ✅ Deploy container
- ✅ Jalankan bot

## Step 3: Setup Environment Variables
1. Di Railway, buka project → **"Variables"**
2. Tambahkan variables ini:

```
BOT_TOKEN=8391302606:AAHJJ0noM8pJAmCAi1LrjY635lzXmM5zYVk
ILOVEPDF_PUBLIC_KEY=your_key_optional
ILOVEPDF_SECRET_KEY=your_secret_optional
```

3. Klik **"Save"**

## Step 4: Redeploy
1. Klik **"Redeploy"** di Railway dashboard
2. Tunggu build & deploy selesai
3. Bot langsung jalan! ✅

---

## ✅ Cek Bot Jalan

Buka Telegram → Kirim message ke bot Anda → Bot harus respond!

---

## 📊 Monitor Bot

Di Railway Dashboard:
- **Logs**: Lihat output bot real-time
- **Metrics**: CPU, Memory usage
- **Status**: Jika red = ada error, cek logs

---

## 🔄 Update Bot

Setiap kali ada update:
```bash
git push origin main
```

Railway otomatis redeploy! 🚀

---

## 💡 Pro Tips

### Keep-Alive (agar tidak sleep)
Jika bot tiba-tiba tidak respond, Railway mungkin sleep bot. Upgrade ke:
- **Hobby Plan** ($5/bulan) = 24/7 non-stop
- Atau gunakan service ping external

### Custom Domain (Opsional)
Railway bisa punya domain custom. Tapi untuk bot Telegram tidak perlu.

### Database Backup
Jika ada user data, setup backup di Project Settings.

---

## 🆘 Troubleshooting

### ❌ Bot tidak jalan
1. Cek **Logs** di Railway
2. Cek **BOT_TOKEN** benar
3. Cek internet connection
4. Redeploy manual

### ❌ Deployment error
1. Cek Dockerfile syntax
2. Cek requirements.txt lengkap
3. Cek bot.py bisa run `python bot.py`

### ❌ Bot timeout
1. Upgrade Railway plan (default shared resources limited)
2. Atau optimize code (reduce processing time)

---

**Selesai! Bot Anda sekarang jalan 24/7 di cloud! 🎉**

Pertanyaan? Cek [DEPLOYMENT.md](DEPLOYMENT.md) untuk opsi lain.
