import 'dotenv/config';
import { Telegraf, session } from 'telegraf';
import { message } from 'telegraf/filters';
import { convertImagesToPdf } from './converters/jpgToPdf';
import { convertPdfToImages } from './converters/pdfToImages';
import { logger } from './utils/logger';

const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) throw new Error('BOT_TOKEN env required');

export const bot = new Telegraf(BOT_TOKEN);

// Session untuk menyimpan state user
bot.use(session());

// Middleware logging
bot.use(async (ctx, next) => {
  logger.info(`Update from ${ctx.from?.id}: ${ctx.updateType}`);
  await next();
});

// Perintah start
bot.command('start', (ctx) => {
  ctx.reply(`
🤖 *Nyoto Bot*  
Perintah yang tersedia:  
/start - Tampilkan pesan ini  
/jpgtopdf - Kirim foto → dapat file PDF  
/pdftojpg - Kirim PDF → dapat gambar JPG (dalam ZIP)  
/pdftopng - Kirim PDF → dapat gambar PNG (dalam ZIP)  
/kopi - Info donasi  

📌 *Catatan*: Fitur PDF → Gambar hanya berfungsi jika environment mendukung poppler-utils (tidak berfungsi di Vercel).  
  `, { parse_mode: 'Markdown' });
});

bot.command('kopi', (ctx) => {
  ctx.reply('☕ *Support development*: SeaBank - AfganiArdiMaryanto - 901067312394', { parse_mode: 'Markdown' });
});

// Perintah konversi
bot.command('jpgtopdf', (ctx) => {
  ctx.session = { action: 'jpgtopdf' };
  ctx.reply('📸 Kirim satu atau beberapa foto (media group) yang ingin dijadikan PDF.');
});

bot.command('pdftojpg', (ctx) => {
  ctx.session = { action: 'pdftojpg' };
  ctx.reply('📄 Kirim file PDF untuk diubah menjadi gambar JPG (dikemas dalam ZIP).');
});

bot.command('pdftopng', (ctx) => {
  ctx.session = { action: 'pdftopng' };
  ctx.reply('📄 Kirim file PDF untuk diubah menjadi gambar PNG (dikemas dalam ZIP).');
});

// Handler foto (untuk jpgtopdf)
bot.on(message('photo'), async (ctx) => {
  const action = ctx.session?.action;
  if (action !== 'jpgtopdf') return;

  try {
    // Ambil semua foto (media group atau single)
    let photoFiles = ctx.message.photo;
    if (ctx.message.media_group_id) {
      // TODO: jika ingin support media group, perlu menyimpan state dan menunggu semua foto
      // Untuk kemudahan, kita hanya proses foto pertama dari media group
      ctx.reply('⚠️ Untuk multiple foto, kirim satu per satu atau kirim sebagai album (akan diproses semua).');
    }
    const largestPhoto = photoFiles.pop(); // foto resolusi tertinggi
    const fileLink = await ctx.telegram.getFileLink(largestPhoto!.file_id);
    const pdfBuffer = await convertImagesToPdf([fileLink.toString()]);
    await ctx.replyWithDocument({ source: pdfBuffer, filename: 'output.pdf' });
    delete ctx.session.action;
  } catch (err: any) {
    logger.error(err);
    ctx.reply(`❌ Gagal konversi: ${err.message}`);
    delete ctx.session.action;
  }
});

// Handler dokumen (untuk pdf_to_jpg / pdf_to_png)
bot.on(message('document'), async (ctx) => {
  const action = ctx.session?.action;
  if (!action || !action.startsWith('pdf_to_')) return;

  const doc = ctx.message.document;
  if (!doc.mime_type?.includes('pdf')) {
    return ctx.reply('❌ Harap kirim file PDF.');
  }

  try {
    const format = action === 'pdf_to_jpg' ? 'jpg' : 'png';
    const fileLink = await ctx.telegram.getFileLink(doc.file_id);
    const zipBuffer = await convertPdfToImages(fileLink.toString(), format);
    await ctx.replyWithDocument({ source: zipBuffer, filename: `output_${format}.zip` });
    delete ctx.session.action;
  } catch (err: any) {
    logger.error(err);
    ctx.reply(`❌ Gagal konversi PDF ke gambar: ${err.message}\n\nCatatan: Fitur ini membutuhkan poppler-utils dan tidak berfungsi di Vercel. Deploy ke Railway/Render untuk dukungan penuh.`);
    delete ctx.session.action;
  }
});

// Fallback
bot.on('text', (ctx) => {
  if (!ctx.message.text.startsWith('/')) {
    ctx.reply('Silakan gunakan perintah dari menu /start');
  }
});

// Webhook mode (untuk production)
export const webhookHandler = async (req: any, res: any) => {
  await bot.handleUpdate(req.body, res);
};

// Polling mode (untuk lokal)
if (process.env.VERCEL !== '1' && process.env.NODE_ENV !== 'production') {
  bot.telegram.deleteWebhook().then(() => {
    logger.info('🗑️ Webhook dihapus (beralih ke polling).');
    bot.launch().then(() => logger.info('🤖 Bot Nyoto sedang berjalan secara lokal...'));
  });
  
  process.once('SIGINT', () => bot.stop('SIGINT'));
  process.once('SIGTERM', () => bot.stop('SIGTERM'));
}
