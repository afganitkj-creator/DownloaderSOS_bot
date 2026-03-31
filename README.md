# 🤖 Telegram File Converter Bot

Bot Telegram sederhana namun tangguh yang dirancang untuk mempermudah konversi dokumen dan gambar langsung dari aplikasi chat Anda. Tidak perlu instalasi tambahan, cukup kirim filenya dan biarkan bot bekerja.

## ✨ Fitur Utama
- **Konversi Cepat**: Mengubah gambar ke PDF atau sebaliknya dalam hitungan detik.
- **Otomasi ZIP**: Jika Anda mengonversi PDF multi-halaman menjadi gambar, bot akan otomatis mengemasnya ke dalam satu file ZIP agar rapi.
- **User Friendly**: Menggunakan sistem perintah `/` yang intuitif.
- **Deteksi Otomatis**: Bot cukup cerdas untuk mengenali alur konversi segera setelah perintah dipilih.

## 🛠 Perintah Menu (Commands)
Anda dapat mengakses fitur bot melalui menu berikut:

| Perintah | Deskripsi |
|---|---|
| `/start` | Menampilkan pesan sambutan dan daftar semua fitur bot. |
| `/jpg_to_pdf` | Konversi satu atau beberapa foto menjadi satu file PDF. |
| `/pdf_to_jpg` | Ekstrak halaman PDF menjadi file gambar berformat JPG. |
| `/pdf_to_png` | Ekstrak halaman PDF menjadi file gambar berformat PNG. || /word_to_pdf | Konversi DOCX ke PDF. |
| /pdf_to_word | Konversi PDF ke DOCX. |
| /excel_to_pdf | Konversi XLSX ke PDF. |
| /pdf_to_excel | Konversi PDF ke XLSX. |
| /ppt_to_pdf | Konversi PPTX ke PDF. |
| /pdf_to_ppt | Konversi PDF ke PPTX. |
| /compress_pdf | Kompres ukuran PDF. |
| /split_pdf | Pecah PDF menjadi halaman terpisah. |
| /merge_pdf | Tambah beberapa PDF untuk digabung. |
| /merge_go | Proses dan unduh PDF gabungan. || `/kopi` | Informasi dukungan/donasi pengembang. |

## 🚀 Cara Penggunaan
1. Buka bot dan ketik/pilih perintah yang diinginkan (contoh: `/pdf_to_jpg`).
2. Bot akan mengirimkan instruksi untuk mengirimkan file yang sesuai.
3. Unggah file PDF atau Gambar Anda.
4. Tunggu proses selesai, bot akan langsung mengirimkan hasil konversinya.

**Catatan**: Untuk konversi PDF ke Gambar dengan banyak halaman, Anda akan menerima satu file `.zip` berisi seluruh hasil konversi.

## ☕ Dukungan & Donasi
Jika bot ini membantu pekerjaan Anda, Anda bisa memberikan dukungan melalui:
- **SeaBank**  
- **No. Rekening**: 901067312394  
- **Atas Nama**: Afgani Ardi Maryanto  

## 📝 Lisensi
Proyek ini dibuat untuk tujuan pembelajaran dan kemudahan akses alat digital. Silakan fork dan kembangkan lebih lanjut.

---

## 🚀 DEPLOYMENT (Jalankan Bot 24/7)

Bot ini bisa dijalankan terus-menerus di cloud tanpa henti! Ada banyak opsi:

### ⭐ **REKOMENDASI: Railway.app (Paling Mudah - GRATIS)**

1. **Buka [railway.app](https://railway.app)** dan login dengan GitHub
2. **"New Project"** → **"Deploy from GitHub Repo"**
3. Pilih repository `DownloaderSOS_bot`
4. Railway otomatis detect `Dockerfile`
5. Setup environment variables di Railway Dashboard:
   - `BOT_TOKEN`: token Telegram bot Anda
   - `ILOVEPDF_PUBLIC_KEY` dan `ILOVEPDF_SECRET_KEY`: (opsional)
6. Deploy! Bot jalan 24/7 ✅

### Opsi Lain:
- **Render.com**: Gratis untuk 18 jam/hari (upgrade untuk 24/7)
- **Docker Compose**: Untuk VPS/Server sendiri
- **GitHub Actions**: Auto-deploy setiap kali push

📖 **Lihat file [DEPLOYMENT.md](DEPLOYMENT.md) untuk panduan lengkap!**

---

## 🐳 Docker (Lokal/Server)

**Jalankan dengan Docker:**
```bash
docker build -t sos-bot .
docker run -d \
  -e BOT_TOKEN="your_token" \
  --restart always \
  --name sos-bot \
  sos-bot
```

**Atau Docker Compose:**
```bash
# Edit .env dengan token Anda
docker-compose up -d
```

---

## 💾 Requirements

- Python 3.11+
- Telegram Bot Token
- (Opsional) iLovePDF API keys untuk kompresi cloud

Semua dependensi sudah tercantum di `requirements.txt`
