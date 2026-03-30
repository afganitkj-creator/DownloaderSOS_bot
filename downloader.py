try:
    import yt_dlp
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Package 'yt-dlp' tidak ditemukan. Jalankan 'pip install yt-dlp' atau 'pip install -r requirements.txt'."
    ) from exc

import os
import time
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "926dc01bbbmsh600fe1df793dbc4p137154jsn8df7d10b19b9")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "ytstream-download-youtube-videos.p.rapidapi.com")

def get_youtube_id(url):
    """Mendapatkan ID Video YouTube dari URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    parsed_url = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(parsed_url.query).get('v', [None])[0]

def get_base_ydl_opts():
    """Mengembalikan konfigurasi dasar yt-dlp beserta Cookies jika tersedia"""
    opts = {
        'noplaylist': True,
        'quiet': True,
    }
    # Membaca file cookies.txt jika dimasukkan oleh user (ampuh tembus blokir YouTube)
    if os.path.exists("cookies.txt"):
        opts['cookiefile'] = "cookies.txt"
    return opts

def get_rapidapi_media(url):
    """Meminta metadata Video dan Audio dari RapidAPI (Youtube-to-Anything)"""
    yt_id = get_youtube_id(url)
    if not yt_id:
        return None
    api_url = f"https://{RAPIDAPI_HOST}/dl?id={yt_id}"
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"RapidAPI error: {e}")
    return None

def get_video_info(url):
    """Mendapatkan metadata video (judul, tumbnail, durasi) dan daftar format yang tersedia."""
    
    # 1. Coba yt-dlp terlebih dahulu (Untuk IG, TikTok, FB, dll yang normal)
    ydl_opts = get_base_ydl_opts()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                        res = f.get('height')
                        if res and res not in [fmt['resolution'] for fmt in formats if 'resolution' in fmt]:
                            formats.append({
                                'type': 'video',
                                'label': f"{res}p (MP4)",
                                'format_id': f"{f['format_id']}+bestaudio/best",
                                'resolution': res
                            })
            
            if not formats:
                formats.append({
                    'type': 'video',
                    'label': 'Best Quality (Video)',
                    'format_id': 'best'
                })
            else:
                formats = sorted(formats, key=lambda x: x.get('resolution', 0), reverse=True)
                
            formats.append({
                'type': 'audio',
                'label': 'Audio Only (MP3/M4A)',
                'format_id': 'bestaudio/best'
            })
            
            return {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration', 0),
                'formats': formats,
                'url': url
            }
    except Exception as e:
        # Jika gagal (seperti blokir Sign-in YouTube) dan URL adalah youtube, pindah ke RapidAPI fallback
        is_youtube = 'youtube.com' in url or 'youtu.be' in url
        if is_youtube:
            api_data = get_rapidapi_media(url)
            if api_data and api_data.get('status') == 'OK':
                title = api_data.get('title', 'YouTube Video')
                formats = []
                
                # Masukkan format video (MP4) dari 'formats'
                for f in api_data.get('formats', []):
                    if 'mimeType' in f and 'video/mp4' in f['mimeType']:
                        q = f.get('qualityLabel', 'Unknown')
                        formats.append({
                            'type': 'video',
                            'label': f"{q} (MP4 - API)",
                            'format_id': f"rapidapi_fmt_{f['itag']}"
                        })
                
                # Masukkan format audio (MP3) dari 'adaptiveFormats'
                for f in api_data.get('adaptiveFormats', []):
                    if 'mimeType' in f and 'audio' in f['mimeType']:
                        ext = 'MP3' if 'webm' not in f['mimeType'] else 'M4A'
                        formats.append({
                            'type': 'audio',
                            'label': f"Audio Only {ext} ({f.get('bitrate', 0)//1000}kbps)",
                            'format_id': f"rapidapi_fmt_{f['itag']}"
                        })
                
                if formats:
                    return {
                        'title': title,
                        'thumbnail': None,
                        'duration': int(api_data.get('lengthSeconds', 0)),
                        'formats': formats,
                        'url': url
                    }
        
        raise Exception(f"Gagal mengambil data media: {str(e)}")

def download_media(url, format_id, type='video', output_dir="tmp/outputs"):
    """Mengunduh media berdasarkan format_id yang dipilih."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Mode eksekusi RapidAPI (Jika format_id diawali 'rapidapi_fmt_')
    if format_id.startswith('rapidapi_fmt_'):
        api_data = get_rapidapi_media(url)
        if not api_data or 'status' not in api_data or api_data['status'] != 'OK':
            raise Exception("RapidAPI gagal memberikan data download.")
            
        itag = format_id.replace('rapidapi_fmt_', '')
        # Cari URL download di formats atau adaptiveFormats
        all_formats = api_data.get('formats', []) + api_data.get('adaptiveFormats', [])
        target = next((f for f in all_formats if str(f.get('itag')) == itag), None)
        
        if not target or 'url' not in target:
            raise Exception("URL download tidak ditemukan di respon API.")
            
        dl_url = target['url']
        safe_title = "".join([c for c in api_data.get('title', 'video') if c.isalnum() or c==' ']).rstrip()
        ext = 'mp4' if type == 'video' else 'mp3'
        filename = f"{output_dir}/nyoto_{safe_title}_{int(time.time())}.{ext}"
        
        # Download manual via requests
        with requests.get(dl_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
        return filename

    # Eksekusi yt-dlp biasa
    filename_template = f"{output_dir}/%(title)s_{int(time.time())}.%(ext)s"
    
    ydl_opts = get_base_ydl_opts()
    ydl_opts['format'] = format_id
    ydl_opts['outtmpl'] = filename_template
    
    # JIka user minta Audio, kita arahkan extension ke m4a atau dipost-processing ke mp3 jika ffmpeg tersedia
    if type == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Unduh dan tunggu
            info_dict = ydl.extract_info(url, download=True)
            
            # Karena postprocessor bisa mengubah ekstensi file (misal m4a ke mp3), filename yang asli perlu didapatkan
            downloaded_file = ydl.prepare_filename(info_dict)
            if type == 'audio':
                 downloaded_file = downloaded_file.rsplit('.', 1)[0] + '.mp3'
                 # Note: fallback ke asli jika ffmpeg tidak terinstal
                 if not os.path.exists(downloaded_file):
                    downloaded_file = ydl.prepare_filename(info_dict)
            
            return downloaded_file
        except Exception as e:
            raise Exception(f"Gagal mengunduh: {str(e)}")
