import fitz  # PyMuPDF
import os
import shutil
import subprocess
import logging
from PIL import Image
from pypdf import PdfReader, PdfWriter

from ilovepdf_client import (
    merge_pdfs_ilovepdf,
    split_pdf_ilovepdf,
    compress_pdf_ilovepdf,
    word_to_pdf_ilovepdf,
    pdf_to_word_ilovepdf
)


def _ensure_dir(path):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def convert_pdf_to_images(pdf_path: str, output_dir: str, format: str = "png") -> list:
    """
    Mengonversi file PDF menjadi daftar file gambar (PNG/JPG).
    Menggunakan PyMuPDF (fitz) yang sangat cepat dan tidak butuh poppler-utils.
    """
    doc = fitz.open(pdf_path)
    image_paths = []
    _ensure_dir(output_dir)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        output_path = os.path.join(output_dir, f"page_{page_num+1}.{format}")
        pix.save(output_path)
        image_paths.append(output_path)

    return image_paths


def convert_images_to_pdf(image_paths: list, output_pdf_path: str) -> str:
    """
    Mengonversi satu atau banyak gambar (JPG/PNG) menjadi satu file PDF.
    """
    if not image_paths:
        raise ValueError("Tidak ada gambar yang diberikan.")

    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    images[0].save(
        output_pdf_path,
        save_all=True,
        append_images=images[1:]
    )

    return output_pdf_path


def _libreoffice_convert(input_path: str, output_dir: str, output_ext: str):
    _ensure_dir(output_dir)
    soffice_bin = shutil.which('soffice') or shutil.which('libreoffice')
    if soffice_bin:
        cmd = [
            soffice_bin,
            '--headless',
            '--norestore',
            '--nofirststartwizard',
            '--nolockcheck',
            '--convert-to', output_ext,
            '--outdir', output_dir,
            input_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                base = os.path.splitext(os.path.basename(input_path))[0]
                output_file = os.path.join(output_dir, f"{base}.{output_ext}")
                if os.path.exists(output_file):
                    return output_file
            # If LibreOffice fails, continue to fallback
        except (subprocess.TimeoutExpired, Exception) as e:
            pass  # Continue to fallback

    # Fallback: gunakan pypandoc untuk dokumen ke PDF
    ext_out = output_ext.lower()
    input_ext = os.path.splitext(input_path)[1].lstrip('.').lower()

    if ext_out == 'pdf' and input_ext in ('docx', 'doc'):
        try:
            import pypandoc
            # Ensure pandoc binary is available
            try:
                subprocess.run(['pandoc', '--version'], capture_output=True, check=True, timeout=5)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Try to download pandoc wheels
                pypandoc.download_pandoc()
            
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.pdf")
            pypandoc.convert_file(input_path, 'pdf', outputfile=output_file)
            if os.path.exists(output_file):
                return output_file
            raise RuntimeError('pypandoc failed to generate output')
        except Exception as exc:
            pass  # Continue to other fallbacks

    if ext_out == 'docx' and input_ext == 'pdf':
        try:
            from pdf2docx import Converter
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.docx")
            cv = Converter(input_path)
            cv.convert(output_file, start=0, end=None)
            cv.close()
            if os.path.exists(output_file):
                return output_file
        except Exception:
            pass  # Continue to other options

    raise EnvironmentError(f"Tidak dapat mengonversi {input_ext} ke {ext_out}. Pastikan LibreOffice atau Pandoc terinstal.")


def word_to_pdf(docx_path: str, output_dir: str = 'tmp/outputs') -> str:
    try:
        output_path = word_to_pdf_ilovepdf(docx_path, output_dir=output_dir)
        if output_path and os.path.exists(output_path):
            return output_path
    except Exception:
        pass
    return _libreoffice_convert(docx_path, output_dir, 'pdf')


def excel_to_pdf(xlsx_path: str, output_dir: str = 'tmp/outputs') -> str:
    try:
        # iLovePDF tidak menyediakan excel->pdf langsung di API; fallback lokal
        pass
    except Exception:
        pass
    return _libreoffice_convert(xlsx_path, output_dir, 'pdf')


def ppt_to_pdf(pptx_path: str, output_dir: str = 'tmp/outputs') -> str:
    try:
        output_path = word_to_pdf_ilovepdf(pptx_path, output_dir=output_dir)
        if output_path and os.path.exists(output_path):
            return output_path
    except Exception:
        pass
    return _libreoffice_convert(pptx_path, output_dir, 'pdf')


def pdf_to_word(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    try:
        output_path = pdf_to_word_ilovepdf(pdf_path, output_dir=output_dir)
        if output_path and os.path.exists(output_path):
            return output_path
    except Exception:
        pass
    return _libreoffice_convert(pdf_path, output_dir, 'docx')


def pdf_to_excel(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pdf_path, output_dir, 'xlsx')


def pdf_to_ppt(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pdf_path, output_dir, 'pptx')


def compress_pdf(input_pdf: str, output_pdf: str) -> str:
    """Kompresi PDF dengan berbagai metode fallback untuk hasil optimal."""
    _ensure_dir(os.path.dirname(output_pdf) or 'tmp/outputs')
    
    # Cek ukuran file input
    input_size = os.path.getsize(input_pdf)
    
    # Method 1: Coba iLovePDF API (cloud-based kompresi)
    try:
        result = compress_pdf_ilovepdf(input_pdf, output_dir=os.path.dirname(output_pdf) or 'tmp/outputs')
        if result.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(result, 'r') as z:
                z.extractall(os.path.dirname(output_pdf) or 'tmp/outputs')
                members = [m for m in z.namelist() if m.lower().endswith('.pdf')]
                if members:
                    extracted = os.path.join(os.path.dirname(output_pdf) or 'tmp/outputs', members[0])
                    os.replace(extracted, output_pdf)
                    if os.path.exists(output_pdf):
                        return output_pdf
        elif os.path.exists(result) and os.path.getsize(result) < input_size:
            os.replace(result, output_pdf)
            return output_pdf
    except Exception as e:
        logging.debug(f"iLovePDF compression failed: {e}")
        pass

    # Method 2: Gunakan Ghostscript untuk kompresi agresif
    gs_bin = shutil.which('gs')
    if gs_bin:
        # Coba beberapa level kompresi Ghostscript
        gs_settings = [
            '/screen',    # Maximum compression (72 dpi, suitable for screen)
            '/ebook',     # Medium compression (150 dpi, suitable for e-reading)
            '/printer',   # Good quality (300 dpi, suitable for printing)
        ]
        
        for quality_setting in gs_settings:
            temp_output = output_pdf + '.gs_temp'
            cmd = [
                gs_bin,
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={quality_setting}',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                '-dDetectDuplicateImages',
                '-r150x150',
                f'-sOutputFile={temp_output}',
                input_pdf
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and os.path.exists(temp_output):
                    temp_size = os.path.getsize(temp_output)
                    # Gunakan hasil jika lebih kecil dari input
                    if temp_size < input_size:
                        os.replace(temp_output, output_pdf)
                        compression_ratio = (1 - temp_size / input_size) * 100
                        logging.info(f"PDF compressed with GS '{quality_setting}': {input_size} → {temp_size} bytes ({compression_ratio:.1f}% reduction)")
                        return output_pdf
                    else:
                        # Coba quality setting berikutnya
                        if os.path.exists(temp_output):
                            os.remove(temp_output)
                        continue
            except (subprocess.TimeoutExpired, Exception) as e:
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                logging.debug(f"GS compression with '{quality_setting}' failed: {e}")
                continue
        
        # Jika tidak ada setting yang sukses, gunakan yang paling agresif
        cmd = [
            gs_bin,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-sOutputFile=' + output_pdf,
            input_pdf
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(output_pdf):
                return output_pdf
        except Exception as e:
            logging.warning(f"Final GS compression attempt failed: {e}")

    # Method 3: Fallback pypdf dengan image compression
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        
        with open(output_pdf, 'wb') as f:
            writer.write(f)
        
        if os.path.exists(output_pdf):
            output_size = os.path.getsize(output_pdf)
            if output_size < input_size:
                compression_ratio = (1 - output_size / input_size) * 100
                logging.info(f"PDF compressed with pypdf: {input_size} → {output_size} bytes ({compression_ratio:.1f}% reduction)")
                return output_pdf
    except Exception as e:
        logging.warning(f"pypdf compression failed: {e}")

    # Method 4: Last resort - Simple copy if no compression possible
    if not os.path.exists(output_pdf):
        shutil.copy2(input_pdf, output_pdf)
        logging.warning("No compression possible, file copied as-is")
    
    return output_pdf


def split_pdf(input_pdf: str, output_dir: str = 'tmp/outputs') -> list:
    try:
        result = split_pdf_ilovepdf(input_pdf, output_dir=output_dir)
        # ilovepdf returns zip path
        if result.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(result, 'r') as z:
                z.extractall(output_dir)
                return [os.path.join(output_dir, m) for m in z.namelist() if m.lower().endswith('.pdf')]
    except Exception:
        pass

    _ensure_dir(output_dir)
    reader = PdfReader(input_pdf)
    output_paths = []

    for idx, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_pdf))[0]}_page_{idx}.pdf")
        with open(out_path, 'wb') as f:
            writer.write(f)
        output_paths.append(out_path)

    return output_paths


def merge_pdfs(input_pdfs: list, output_pdf: str) -> str:
    try:
        result = merge_pdfs_ilovepdf(input_pdfs, output_dir=os.path.dirname(output_pdf) or 'tmp/outputs')
        if os.path.exists(result):
            # if ilovepdf returns ZIP, extract first PDF
            if result.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(result, 'r') as z:
                    z.extractall(os.path.dirname(output_pdf) or 'tmp/outputs')
                    members = [m for m in z.namelist() if m.lower().endswith('.pdf')]
                    if members:
                        return os.path.join(os.path.dirname(output_pdf) or 'tmp/outputs', members[0])
            return result
    except Exception:
        pass

    writer = PdfWriter()
    for pdf_path in input_pdfs:
        reader = PdfReader(pdf_path)
        for p in reader.pages:
            writer.add_page(p)
    _ensure_dir(os.path.dirname(output_pdf))
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    return output_pdf

