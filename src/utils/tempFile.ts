import fs from 'fs/promises';
import path from 'path';
import os from 'os';

export async function createTempDir(): Promise<string> {
  const prefix = 'nyoto-pdf-';
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), prefix));
  return tempDir;
}

export async function cleanupTempDir(dirPath: string): Promise<void> {
  try {
    await fs.rm(dirPath, { recursive: true, force: true });
  } catch (err) {
    console.error(`Failed to cleanup temp dir ${dirPath}:`, err);
  }
}
