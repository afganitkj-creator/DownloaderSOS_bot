import fitz  # PyMuPDF
import os
import shutil
import subprocess
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
            '--convert-to', output_ext,
            '--outdir', output_dir,
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Konversi LibreOffice gagal: {result.stderr.strip()}")

        base = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(output_dir, f"{base}.{output_ext}")

    # Fallback: tanpa LibreOffice, gunakan library Python jika tersedia
    ext_out = output_ext.lower()
    input_ext = os.path.splitext(input_path)[1].lstrip('.').lower()

    if ext_out == 'pdf' and input_ext in ('docx', 'doc'):
        # docx2pdf tidak berjalan di Linux kecuali memiliki MS Word, jadi coba pypandoc sebagai opsi
        try:
            import pypandoc
        except ImportError:
            raise EnvironmentError("LibreOffice tidak ditemukan dan pypandoc belum terpasang; install LibreOffice atau pypandoc.")

        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.pdf")
        try:
            pypandoc.convert_file(input_path, 'pdf', outputfile=output_file)
            if os.path.exists(output_file):
                return output_file
            raise RuntimeError('pypandoc gagal menghasilkan output file')
        except Exception as exc:
            raise RuntimeError(f"pypandoc error: {exc}")

    if ext_out == 'docx' and input_ext == 'pdf':
        try:
            from pdf2docx import Converter
        except ImportError:
            raise EnvironmentError("LibreOffice tidak ditemukan dan pdf2docx belum terpasang; install LibreOffice atau pdf2docx.")

        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.docx")
        try:
            cv = Converter(input_path)
            cv.convert(output_file, start=0, end=None)
            cv.close()
            if not os.path.exists(output_file):
                raise RuntimeError('pdf2docx gagal menghasilkan output file.')
            return output_file
        except Exception as exc:
            raise RuntimeError(f"pdf2docx error: {exc}")

    raise EnvironmentError("LibreOffice tidak ditemukan; install 'soffice' untuk konversi dokumen.")


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
                    return output_pdf
        elif os.path.exists(result):
            os.replace(result, output_pdf)
            return output_pdf
    except Exception:
        pass

    if shutil.which('gs'):
        cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-sOutputFile=' + output_pdf,
            input_pdf
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Ghostscript compress PDF error: {result.stderr.strip()}")
        return output_pdf

    # fallback tanpa gs: export ulang dengan pypdf
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    with open(output_pdf, 'wb') as f:
        writer.write(f)
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

