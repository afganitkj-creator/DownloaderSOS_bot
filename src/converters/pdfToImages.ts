import poppler from 'pdf-poppler';
import path from 'path';
import fs from 'fs/promises';
import axios from 'axios';
import archiver from 'archiver';
import { createTempDir, cleanupTempDir } from '../utils/tempFile';

export async function convertPdfToImages(pdfUrl: string, format: 'jpg' | 'png'): Promise<Buffer> {
  const tmpDir = await createTempDir();
  const pdfPath = path.join(tmpDir, 'input.pdf');

  try {
    // Download PDF
    const response = await axios.get(pdfUrl, { responseType: 'arraybuffer' });
    await fs.writeFile(pdfPath, response.data);

    const opts = {
      format: format === 'jpg' ? 'jpeg' : 'png',
      out_dir: tmpDir,
      out_prefix: 'page',
      page: null, // all pages
    };
    await poppler.convert(pdfPath, opts);

    // Cari semua file gambar yang dihasilkan
    const files = await fs.readdir(tmpDir);
    const imageFiles = files.filter(f => f.endsWith(`.${format === 'jpg' ? 'jpg' : 'png'}`));
    if (imageFiles.length === 0) throw new Error('No image files generated');

    // Zip semua gambar
    const zipBuffer = await createZip(imageFiles.map(f => path.join(tmpDir, f)));
    return zipBuffer;
  } finally {
    await cleanupTempDir(tmpDir);
  }
}

function createZip(filePaths: string[]): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    const archive = archiver('zip', { zlib: { level: 9 } });
    archive.on('data', (chunk) => chunks.push(chunk));
    archive.on('end', () => resolve(Buffer.concat(chunks)));
    archive.on('error', reject);
    for (const file of filePaths) {
      archive.file(file, { name: path.basename(file) });
    }
    archive.finalize();
  });
}
