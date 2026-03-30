import fitz  # PyMuPDF
import os
from PIL import Image

def convert_pdf_to_images(pdf_path: str, output_dir: str, format: str = "png") -> list:
    """
    Mengonversi file PDF menjadi daftar file gambar (PNG/JPG).
    Menggunakan PyMuPDF (fitz) yang sangat cepat dan tidak butuh poppler-utils.
    """
    doc = fitz.open(pdf_path)
    image_paths = []
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # DPI 150 cukup jernih dan ukuran filenya optimal
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
        # Convert ke RGB (menghindari error transparency PNG saat disave ke PDF)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
        
    # Simpan sebagai single PDF multi-halaman
    images[0].save(
        output_pdf_path, 
        save_all=True, 
        append_images=images[1:]
    )
    
    return output_pdf_path
