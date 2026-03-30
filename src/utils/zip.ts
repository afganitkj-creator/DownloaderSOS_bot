import archiver from 'archiver';
import path from 'path';

/**
 * Creates a ZIP buffer from an array of file paths.
 */
export function createZip(filePaths: string[]): Promise<Buffer> {
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
