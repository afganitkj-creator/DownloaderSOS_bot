import os
import shutil
import time
import re
import logging
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from core import (
    convert_pdf_to_images,
    convert_images_to_pdf,
    word_to_pdf,
    pdf_to_word,
    excel_to_pdf,
    pdf_to_excel,
    ppt_to_pdf,
    pdf_to_ppt,
    compress_pdf,
    split_pdf,
    merge_pdfs
)
from downloader import get_video_info, download_media

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Token bot tidak ditemukan di .env!")

logging.info(f"Memuat token bot: {BOT_TOKEN[:10]}***")

# Folder temporary untuk bot khusus
os.makedirs("tmp/bot_uploads", exist_ok=True)
os.makedirs("tmp/bot_outputs", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/start diterima dari user {update.effective_user.id} ({update.effective_user.username})")
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

async def word_to_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'word_to_pdf'
    await update.message.reply_text('📄 Kirim file DOCX untuk dikonversi menjadi PDF.')

async def pdf_to_word_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'pdf_to_word'
    await update.message.reply_text('📄 Kirim file PDF untuk dikonversi menjadi DOCX.')

async def excel_to_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'excel_to_pdf'
    await update.message.reply_text('📄 Kirim file XLSX untuk dikonversi menjadi PDF.')

async def pdf_to_excel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'pdf_to_excel'
    await update.message.reply_text('📄 Kirim file PDF untuk dikonversi menjadi XLSX.')

async def ppt_to_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'ppt_to_pdf'
    await update.message.reply_text('📄 Kirim file PPTX untuk dikonversi menjadi PDF.')

async def pdf_to_ppt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'pdf_to_ppt'
    await update.message.reply_text('📄 Kirim file PDF untuk dikonversi menjadi PPTX.')

async def compress_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'compress_pdf'
    await update.message.reply_text('📄 Kirim file PDF yang ingin dikompres.')

async def split_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'split_pdf'
    await update.message.reply_text('📄 Kirim file PDF yang ingin dipecah per halaman.')

async def merge_pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = 'merge_pdf'
    context.user_data['merge_files'] = []
    await update.message.reply_text('📄 Kirim beberapa file PDF (1 per pesan), lalu kirim /merge_go setelah selesai.')

async def merge_pdf_go_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = context.user_data.get('merge_files', [])
    if len(files) < 2:
        await update.message.reply_text('❌ Perlu minimal 2 file PDF untuk merge.')
        return
    output_path = os.path.join('tmp/bot_outputs', f'merged_{int(time.time())}.pdf')
    result = merge_pdfs(files, output_path)
    with open(result, 'rb') as f:
        await update.message.reply_document(document=f, filename=os.path.basename(result))
    context.user_data.pop('merge_files', None)
    context.user_data.pop('action', None)

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
    doc = update.message.document
    if not doc:
        return

    file = await context.bot.get_file(doc.file_id)
    input_path = os.path.join("tmp/bot_uploads", f"{doc.file_id}_{doc.file_name}")
    os.makedirs("tmp/bot_uploads", exist_ok=True)
    await file.download_to_drive(input_path)

    out_dir = os.path.join("tmp/bot_outputs")
    os.makedirs(out_dir, exist_ok=True)

    try:
        if action in ['pdftojpg', 'pdftopng']:
            if doc.mime_type != 'application/pdf':
                await update.message.reply_text("❌ Harap kirim file PDF.")
                return
            await update.message.reply_text('⏳ Sedang mengekstrak halaman PDF menjadi gambar...')
            fmt = 'jpg' if action == 'pdftojpg' else 'png'
            image_paths = convert_pdf_to_images(input_path, os.path.join(out_dir, f"extracted_{doc.file_id}"), format=fmt)

            for i in range(0, len(image_paths), 10):
                chunk = image_paths[i:i+10]
                media_group = [InputMediaPhoto(media=open(img, 'rb')) for img in chunk]
                await update.message.reply_media_group(media=media_group)

            context.user_data.pop('action', None)

        elif action == 'word_to_pdf':
            output_path = word_to_pdf(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'pdf_to_word':
            output_path = pdf_to_word(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'excel_to_pdf':
            output_path = excel_to_pdf(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'pdf_to_excel':
            output_path = pdf_to_excel(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'ppt_to_pdf':
            output_path = ppt_to_pdf(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'pdf_to_ppt':
            output_path = pdf_to_ppt(input_path, out_dir)
            await update.message.reply_document(document=open(output_path, 'rb'), filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'compress_pdf':
            output_path = os.path.join(out_dir, f"compressed_{os.path.basename(input_path)}")
            input_size = os.path.getsize(input_path)
            compress_pdf(input_path, output_path)
            output_size = os.path.getsize(output_path)
            reduction = (1 - output_size / input_size) * 100 if input_size > 0 else 0
            
            # Send info message with compression stats
            size_before = f"{input_size / 1024 / 1024:.2f} MB" if input_size > 1024*1024 else f"{input_size / 1024:.2f} KB"
            size_after = f"{output_size / 1024 / 1024:.2f} MB" if output_size > 1024*1024 else f"{output_size / 1024:.2f} KB"
            info_msg = f"📊 *Kompresi PDF Selesai*\n📥 Ukuran awal: {size_before}\n📤 Ukuran akhir: {size_after}\n✂️ Pengurangan: {reduction:.1f}%"
            await update.message.reply_text(info_msg, parse_mode='Markdown')
            
            # Send compressed file
            with open(output_path, 'rb') as f:
                await update.message.reply_document(document=f, filename=os.path.basename(output_path))
            context.user_data.pop('action', None)

        elif action == 'split_pdf':
            split_paths = split_pdf(input_path, out_dir)
            zip_path = shutil.make_archive(os.path.splitext(os.path.join(out_dir, f'split_{int(time.time())}'))[0], 'zip', out_dir)
            await update.message.reply_document(document=open(zip_path, 'rb'), filename=os.path.basename(zip_path))
            context.user_data.pop('action', None)

        elif action == 'merge_pdf':
            merge_list = context.user_data.setdefault('merge_files', [])
            if doc.mime_type != 'application/pdf':
                await update.message.reply_text("❌ File harus PDF untuk merge.")
                return
            merge_list.append(input_path)
            await update.message.reply_text(f"✅ PDF ditambahkan ({len(merge_list)}) - kirim /merge_go saat siap.")

        else:
            # Jika tidak ada action yang dikenali, proses default tetap pdftojpg/png
            await update.message.reply_text("⚠️ Aksi tidak dikenali. Gunakan perintah yang tersedia.")

    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if 'pandoc' in error_msg.lower():
            user_msg = '❌ Gagal mengonversi: Pandoc tidak bisa dijalankan. Coba lagi.'
        elif 'soffice' in error_msg.lower() or 'libreoffice' in error_msg.lower():
            user_msg = '❌ Gagal mengonversi: LibreOffice tidak bisa dijalankan. Coba lagi.'
        elif 'Tidak dapat mengonversi' in error_msg:
            user_msg = f'❌ Gagal: {error_msg}'
        else:
            user_msg = f'❌ Gagal memproses dokumen: {error_msg[:100]}'
        
        await update.message.reply_text(user_msg)
        logging.error(f'Error for user {update.effective_user.id}: {error_msg}', exc_info=True)

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
        ("word_to_pdf", "DOCX -> PDF"),
        ("pdf_to_word", "PDF -> DOCX"),
        ("excel_to_pdf", "XLSX -> PDF"),
        ("pdf_to_excel", "PDF -> XLSX"),
        ("ppt_to_pdf", "PPTX -> PDF"),
        ("pdf_to_ppt", "PDF -> PPTX"),
        ("compress_pdf", "Kompres PDF"),
        ("split_pdf", "Split PDF"),
        ("merge_pdf", "Kumpulkan beberapa PDF"),
        ("merge_go", "Selesaikan merge PDF"),
        ("kopi", "Dukungan & Donasi")
    ])

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kopi", kopi))
    app.add_handler(CommandHandler("jpgtopdf", jpgtopdf_cmd))
    app.add_handler(CommandHandler("pdftojpg", pdftojpg_cmd))
    app.add_handler(CommandHandler("pdftopng", pdftopng_cmd))

    app.add_handler(CommandHandler("word_to_pdf", word_to_pdf_cmd))
    app.add_handler(CommandHandler("pdf_to_word", pdf_to_word_cmd))
    app.add_handler(CommandHandler("excel_to_pdf", excel_to_pdf_cmd))
    app.add_handler(CommandHandler("pdf_to_excel", pdf_to_excel_cmd))
    app.add_handler(CommandHandler("ppt_to_pdf", ppt_to_pdf_cmd))
    app.add_handler(CommandHandler("pdf_to_ppt", pdf_to_ppt_cmd))
    app.add_handler(CommandHandler("compress_pdf", compress_pdf_cmd))
    app.add_handler(CommandHandler("split_pdf", split_pdf_cmd))
    app.add_handler(CommandHandler("merge_pdf", merge_pdf_cmd))
    app.add_handler(CommandHandler("merge_go", merge_pdf_go_cmd))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Bot Telegram (Python Edition) siap melayani dan sedang melakukan polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
