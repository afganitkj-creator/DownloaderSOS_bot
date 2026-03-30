import PDFDocument from 'pdfkit';
import sharp from 'sharp';
import axios from 'axios';

export async function convertImagesToPdf(imageUrls: string[]): Promise<Buffer> {
  return new Promise(async (resolve, reject) => {
    const doc = new PDFDocument({ autoFirstPage: false });
    const buffers: Buffer[] = [];
    doc.on('data', buffers.push.bind(buffers));
    doc.on('end', () => resolve(Buffer.concat(buffers)));
    doc.on('error', reject);

    for (const url of imageUrls) {
      const response = await axios.get(url, { responseType: 'arraybuffer' });
      const imgBuffer = Buffer.from(response.data);
      const { width, height } = await sharp(imgBuffer).metadata();
      doc.addPage({ size: [width!, height!] });
      doc.image(imgBuffer, 0, 0, { width: width!, height: height! });
    }
    doc.end();
  });
}
