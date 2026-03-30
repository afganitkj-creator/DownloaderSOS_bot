import fitz  # PyMuPDF
import os
import shutil
import subprocess
from PIL import Image
from pypdf import PdfReader, PdfWriter


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
    if shutil.which('soffice'):
        binname = 'soffice'
    elif shutil.which('libreoffice'):
        binname = 'libreoffice'
    else:
        raise EnvironmentError("LibreOffice tidak ditemukan; install 'soffice' untuk konversi dokumen.")

    cmd = [
        binname,
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


def word_to_pdf(docx_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(docx_path, output_dir, 'pdf')


def excel_to_pdf(xlsx_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(xlsx_path, output_dir, 'pdf')


def ppt_to_pdf(pptx_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pptx_path, output_dir, 'pdf')


def pdf_to_word(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pdf_path, output_dir, 'docx')


def pdf_to_excel(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pdf_path, output_dir, 'xlsx')


def pdf_to_ppt(pdf_path: str, output_dir: str = 'tmp/outputs') -> str:
    return _libreoffice_convert(pdf_path, output_dir, 'pptx')


def compress_pdf(input_pdf: str, output_pdf: str) -> str:
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
    writer = PdfWriter()
    for pdf_path in input_pdfs:
        reader = PdfReader(pdf_path)
        for p in reader.pages:
            writer.add_page(p)
    _ensure_dir(os.path.dirname(output_pdf))
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    return output_pdf

