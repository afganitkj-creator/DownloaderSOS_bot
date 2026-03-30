import os
import shutil
import time
import re
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from core import convert_pdf_to_images, convert_images_to_pdf
from downloader import get_video_info, download_media

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Token bot tidak ditemukan di .env!")

# Folder temporary untuk bot khusus
os.makedirs("tmp/bot_uploads", exist_ok=True)
os.makedirs("tmp/bot_outputs", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *Nyoto Bot (Python Edition)*\n"
        "Perintah yang tersedia:\n"
        "/start - Tampilkan pesan ini\n"
        "/jpgtopdf - Kirim foto → dapat file PDF\n"
        "/pdftojpg - Kirim PDF → Ekstrak ke JPG\n"
        "/pdftopng - Kirim PDF → Ekstrak ke PNG\n"
        "/kopi - Sahabat Developer\n\n"
        "📥 *Sosmed Downloader*\n"
        "Kirimkan saja link YouTube, TikTok, Instagram, atau X (Twitter), dan bot ini akan ajaib mengunduhnya untukmu!"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def kopi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("☕ *Support development*: SeaBank - AfganiArdiMaryanto - 901067312394", parse_mode='Markdown')

async def jpgtopdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'jpgtopdf'
    await update.message.reply_text('📸 Kirim satu foto (atau beberapa foto sebagai album) yang ingin dijadikan PDF.')

async def pdftojpg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'pdftojpg'
    await update.message.reply_text('📄 Kirim file PDF untuk diubah menjadi kumpulan gambar JPG.')

async def pdftopng_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'pdftopng'
    await update.message.reply_text('📄 Kirim file PDF untuk diubah menjadi kumpulan gambar PNG.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get('action')
    if action != 'jpgtopdf':
        return
        
    loading_msg = await update.message.reply_text('⏳ Sedang memproses menjadi PDF, mohon tunggu...')
    
    # Ambil resolusi terbesar dari foto yang dikirim
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    photo_path = os.path.join("tmp/bot_uploads", f"{photo.file_id}.jpg")
    await file.download_to_drive(photo_path)
    
    output_pdf = os.path.join("tmp/bot_outputs", f"output_{update.message.message_id}.pdf")
    try:
        convert_images_to_pdf([photo_path], output_pdf)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=loading_msg.message_id)
        
        with open(output_pdf, 'rb') as f:
            await update.message.reply_document(document=f, filename="output.pdf")
            
        context.user_data.pop('action', None)
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get('action')
    if action not in ['pdftojpg', 'pdftopng']:
        return
        
    doc = update.message.document
    if doc.mime_type != 'application/pdf':
        await update.message.reply_text("❌ Harap kirim file PDF.")
        return
        
    loading_msg = await update.message.reply_text('⏳ Sedang mengekstrak halaman PDF menjadi gambar tanpa distorsi, mohon tunggu...')
    
    file = await context.bot.get_file(doc.file_id)
    pdf_path = os.path.join("tmp/bot_uploads", f"{doc.file_id}.pdf")
    await file.download_to_drive(pdf_path)
    
    out_dir = os.path.join("tmp/bot_outputs", f"extracted_{doc.file_id}")
    fmt = "jpg" if action == "pdftojpg" else "png"
    
    try:
        image_paths = convert_pdf_to_images(pdf_path, out_dir, format=fmt)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=loading_msg.message_id)
        
        if not image_paths:
            await update.message.reply_text("❌ Tidak ada gambar yang berhasil diekstrak.")
            return
            
        # Kirim secara massal sebagai album Telegram (maks 10 per pesan)
        for i in range(0, len(image_paths), 10):
            chunk = image_paths[i:i+10]
            media_group = [InputMediaPhoto(media=open(img, 'rb')) for img in chunk]
            await update.message.reply_media_group(media=media_group)
            
        context.user_data.pop('action', None)
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal merender PDF: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    
    # Check if it's a URL
    url_pattern = re.compile(r'https?://[^\s]+')
    match = url_pattern.search(text)
    
    if match:
        url = match.group(0)
        loading_msg = await update.message.reply_text('⏳ Memindai Sosmed Link...')
        try:
            info = get_video_info(url)
            
            # Save info to user_data mapped by message_id so callback can access it
            context.user_data[loading_msg.message_id] = info
            
            keyboard = []
            for idx, f in enumerate(info['formats']):
                cb_data = f"dl|{loading_msg.message_id}|{idx}"
                keyboard.append([InlineKeyboardButton(f['label'], callback_data=cb_data)])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=loading_msg.message_id,
                text=f"🎥 **{info['title']}**\n⏱️ Durasi: {info['duration']}s\n\nPilih format unduhan:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
             await context.bot.edit_message_text(
                 chat_id=update.effective_chat.id,
                 message_id=loading_msg.message_id,
                 text=f"❌ Gagal mengenali media dari link: {e}"
             )
    else:
        if not text.startswith('/'):
            await update.message.reply_text("Kirimkan foto/PDF untuk dikonversi, atau kirim URL untuk didownload.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("dl|"):
        parts = data.split("|")
        msg_id, format_idx = int(parts[1]), int(parts[2])
        
        info = context.user_data.get(msg_id)
        if not info:
            await query.edit_message_text("❌ Sesi kadaluarsa. Silakan kirimkan ulang link-nya.")
            return
            
        selected_format = info['formats'][format_idx]
        
        await query.edit_message_text("⏳ Sedang mengunduh file media ke bot, mohon bersabar...")
        try:
            os.makedirs("tmp/bot_downloads", exist_ok=True)
            filepath = download_media(info['url'], selected_format['format_id'], type=selected_format['type'], output_dir="tmp/bot_downloads")
            
            await query.edit_message_text("✅ Mengunggah ke Telegram... (Tergantung ukuran file)")
            
            if selected_format['type'] == 'video':
                with open(filepath, 'rb') as f:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=info['title'])
            else:
                with open(filepath, 'rb') as f:
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, title=info['title'])
                    
            await query.edit_message_text(f"✅ Sukses terkirim: {info['title']}")
        except Exception as e:
            await query.edit_message_text(f"❌ Telegram gagal memproses file ini (Mungkin terlalu besar >50MB): {e}")

async def post_init(application: Application):
    await application.bot.set_my_commands([
        ("start", "Tampilkan pesan bantuan"),
        ("jpgtopdf", "Kirim foto -> dapat file PDF"),
        ("pdftojpg", "Kirim PDF -> dapat gambar JPG"),
        ("pdftopng", "Kirim PDF -> dapat gambar PNG"),
        ("kopi", "Dukungan & Donasi")
    ])

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kopi", kopi))
    app.add_handler(CommandHandler("jpgtopdf", jpgtopdf_cmd))
    app.add_handler(CommandHandler("pdftojpg", pdftojpg_cmd))
    app.add_handler(CommandHandler("pdftopng", pdftopng_cmd))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Bot Telegram (Python Edition) siap melayani dan sedang melakukan polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
