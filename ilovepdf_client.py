import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ILOVEPDF_PUBLIC_KEY = os.getenv("ILOVEPDF_PUBLIC_KEY")
ILOVEPDF_SECRET_KEY = os.getenv("ILOVEPDF_SECRET_KEY")
BASE_URL = "https://api.ilovepdf.com/v1"


def _assert_keys():
    if not ILOVEPDF_PUBLIC_KEY or not ILOVEPDF_SECRET_KEY:
        raise EnvironmentError("ILovePDF API key tidak ditemukan di .env; set ILOVEPDF_PUBLIC_KEY dan ILOVEPDF_SECRET_KEY")


def _auth_headers():
    _assert_keys()
    return {
        'Authorization': f'Bearer {ILOVEPDF_SECRET_KEY}'
    }


def _new_task(tool):
    _assert_keys()
    resp = requests.post(f"{BASE_URL}/task/new", json={
        'tool': tool,
        'public_key': ILOVEPDF_PUBLIC_KEY
    })
    resp.raise_for_status()
    return resp.json()['task']


def _upload(task, file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'task': task,
            'public_key': ILOVEPDF_PUBLIC_KEY,
            'signature': ILOVEPDF_SECRET_KEY
        }
        resp = requests.post(f"{BASE_URL}/task/{task}/upload", data=data, files=files)
        resp.raise_for_status()
    return resp.json()


def _process(task, params):
    resp = requests.post(f"{BASE_URL}/task/{task}/process", json=params)
    resp.raise_for_status()
    return resp.json()


def _download(task, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    resp = requests.get(f"{BASE_URL}/task/{task}/download", stream=True)
    resp.raise_for_status()

    output_file = os.path.join(output_dir, f"ilovepdf_{task}_{int(time.time())}.zip")
    with open(output_file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return output_file


def ilovepdf_task(tool, paths, params=None, output_dir='tmp/outputs'):
    _assert_keys()
    task = _new_task(tool)

    if isinstance(paths, str):
        paths = [paths]

    for path in paths:
        _upload(task, path)

    cfg = {
        'task': task,
        'tool': tool,
        'public_key': ILOVEPDF_PUBLIC_KEY,
        'signature': ILOVEPDF_SECRET_KEY,
        'files': [{'filename': os.path.basename(p)} for p in paths]
    }

    if params:
        cfg.update(params)

    _process(task, cfg)
    return _download(task, output_dir)


def merge_pdfs_ilovepdf(paths, output_dir='tmp/outputs'):
    return ilovepdf_task('merge', paths, output_dir=output_dir)


def split_pdf_ilovepdf(path, output_dir='tmp/outputs'):
    return ilovepdf_task('split', path, output_dir=output_dir)


def compress_pdf_ilovepdf(path, output_dir='tmp/outputs'):
    return ilovepdf_task('compress', path, output_dir=output_dir)


def word_to_pdf_ilovepdf(path, output_dir='tmp/outputs'):
    return ilovepdf_task('officepdf', path, output_dir=output_dir)


def pdf_to_word_ilovepdf(path, output_dir='tmp/outputs'):
    return ilovepdf_task('pdftoword', path, output_dir=output_dir)
