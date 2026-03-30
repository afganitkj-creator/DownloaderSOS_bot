import streamlit as st
import os
import shutil
import time
from core import (
    convert_pdf_to_images,
    convert_images_to_pdf,
    word_to_pdf,
    pdf_to_word,
    excel_to_pdf,
    pdf_to_excel,
    ppt_to_pdf,
    pdf_to_ppt,
    compress_pdf,
    split_pdf,
    merge_pdfs,
    _ensure_dir
)
from downloader import get_video_info, download_media

st.set_page_config(page_title="Nyoto Studio", page_icon="🎨", layout="wide")

st.markdown("""
<style>
    /* Custom Styling untuk Canvas yang artistik */
    .main .block-container {
        padding-top: 3rem;
        max-width: 950px;
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#ff7e5f, #feb47b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        margin-bottom: 0px;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #ff7e5f;
        border-radius: 12px;
        padding: 15px;
        background-color: #fff9f6;
    }
    .stDownloadButton button {
        background-color: #ff7e5f !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stDownloadButton button:hover {
        background-color: #ff6842 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Nyoto Studio 🎨")
st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #666;'>Ubah Gambar ke PDF, Ekstrak PDF, atau Download Video/Audio dari Sosmed.</p>", unsafe_allow_html=True)
st.markdown("---")

# Siapkan folder sementara
os.makedirs("tmp/uploads", exist_ok=True)
os.makedirs("tmp/outputs", exist_ok=True)
os.makedirs("tmp/downloads", exist_ok=True)

tab1, tab2, tab3 = st.tabs(["📸 Jadikan PDF", "📄 Ekstrak PDF", "📥 Sosmed Downloader"])

with tab1:
    st.markdown("### Konversi Kumpulan Gambar menjadi Dokumen PDF")
    uploaded_images = st.file_uploader("Seret dan taruh foto (JPG/PNG) di sini", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_images and st.button("🪄 Rangkai menjadi PDF", key="btn_img_pdf", use_container_width=True):
        with st.spinner("⏳ Sedang memproses gambarmu layaknya *magic*..."):
            saved_paths = []
            for img in uploaded_images:
                path = os.path.join("tmp/uploads", img.name)
                with open(path, "wb") as f:
                    f.write(img.getbuffer())
                saved_paths.append(path)
                
            output_pdf = os.path.join("tmp/outputs", f"nyoto_output_{int(time.time())}.pdf")
            try:
                convert_images_to_pdf(saved_paths, output_pdf)
                st.success("✅ Dokumen PDF Berhasil Dibuat!")
                with open(output_pdf, "rb") as f:
                    st.download_button(
                        label="⬇️ Unduh Dokumen PDF",
                        data=f,
                        file_name="hasil_konversi_nyoto.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Gagal memproses: {e}")

with tab2:
    st.markdown("### Bongkar Dokumen PDF menjadi Kumpulan Gambar Asli")
    uploaded_pdf = st.file_uploader("Seret file PDF yang mau dibongkar ke kotak ini", type=["pdf"], accept_multiple_files=False)
    format_choice = st.radio("Format gambar yang diinginkan:", ("jpg", "png"), horizontal=True)
    
    if uploaded_pdf and st.button("🪄 Ekstrak Halaman", key="btn_pdf_img", use_container_width=True):
        with st.spinner("⏳ Membongkar halaman PDF jadi kanvas gambar..."):
            pdf_path = os.path.join("tmp/uploads", uploaded_pdf.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
                
            output_folder = os.path.join("tmp/outputs", f"extracted_{int(time.time())}")
            try:
                image_paths = convert_pdf_to_images(pdf_path, output_folder, format=format_choice)
                st.success(f"✅ Ekstraksi selesai! PDF ini memiliki {len(image_paths)} halaman.")
                
                # Base nama file original tanpa ekstensi PDF
                original_name = os.path.splitext(uploaded_pdf.name)[0]
                
                st.markdown("### 🖼️ Hasil Kanvas Gambar")
                
                # Menggunakan layout kolom untuk galerinya
                cols = st.columns(3)
                for idx, img_p in enumerate(image_paths):
                    col = cols[idx % 3]
                    with col:
                        # Kanvas Gambar
                        st.image(img_p, use_container_width=True)
                        
                        # Nama file download spesifik menulari aslinya
                        download_filename = f"{original_name}-halaman-{idx+1}.{format_choice}"
                        
                        # Tombol Download individu
                        with open(img_p, "rb") as f:
                            st.download_button(
                                label=f"⬇️ Unduh Hal {idx+1}",
                                data=f,
                                file_name=download_filename,
                                mime=f"image/{format_choice}",
                                key=f"dl_single_{idx}",
                                use_container_width=True
                            )
                
                st.markdown("---")
                # ZIP Fallback yang rapih
                zip_path = shutil.make_archive(output_folder, 'zip', output_folder)
                st.info("💡 Butuh download seluruh kanvasnya sekaligus? Gunakan opsi format arsip .ZIP di bawah ini:")
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="📦 Unduh Seluruh Halaman (Format ZIP)",
                        data=f,
                        file_name=f"{original_name}_lengkap.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Gagal memproses PDF: {e}")

with tab3:
    st.markdown("### Unduh Video / Audio dari YouTube, IG, TikTok, X")
    st.info("💡 Tempelkan link postingan/video dari sosial media di bawah ini.")
    
    url_input = st.text_input("🔗 Masukkan Link URL (Contoh: https://youtu.be/... ata tiktok.com/...)")
    
    if url_input:
        if st.button("🔍 Cek Link", use_container_width=True):
            with st.spinner("⏳ Sedang mengambil info video..."):
                try:
                    info = get_video_info(url_input)
                    st.session_state['media_info'] = info
                except Exception as e:
                    st.error(str(e))
    
    # Jika info video sudah dimuat di session
    if 'media_info' in st.session_state and st.session_state['media_info']['url'] == url_input:
        info = st.session_state['media_info']
        
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        with col1:
            if info['thumbnail']:
                st.image(info['thumbnail'], use_container_width=True)
        with col2:
            st.markdown(f"**Judul:** {info['title']}")
            st.markdown(f"**Durasi:** {info['duration']} detik")
            
            # Pilihan format
            # formats adalah list dictionary {type, label, format_id, res}
            format_options = {f['label']: f for f in info['formats']}
            selected_label = st.selectbox("Pilih Kualitas / Format", list(format_options.keys()))
            selected_format = format_options[selected_label]
            
            if st.button("🚀 Unduh Sekarang", type="primary", use_container_width=True):
                with st.spinner("⏳ Sedang mengunduh file, jangan tutup halaman ini..."):
                    try:
                        filepath = download_media(info['url'], selected_format['format_id'], type=selected_format['type'], output_dir="tmp/downloads")
                        st.success("✅ Download Berhasil!")
                        
                        # Siapkan tombol download browser
                        with open(filepath, "rb") as f:
                            st.download_button(
                                label="⬇️ Simpan File ke Perangkat",
                                data=f,
                                file_name=os.path.basename(filepath),
                                mime="video/mp4" if selected_format['type'] == 'video' else "audio/mpeg",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Gagal mengunduh: {str(e)}")
with st.expander('📄 Office & PDF Utility (Word/Excel/PPT <-> PDF, split/merge/compress)', expanded=False):
    st.info("💡 Untuk fitur konversi dokumen, pastikan API key iLovePDF diatur di .env (ILOVEPDF_PUBLIC_KEY dan ILOVEPDF_SECRET_KEY). Jika tidak, akan menggunakan fallback lokal.")
    operation = st.selectbox('Pilih operasi', [
        'word_to_pdf', 'pdf_to_word', 'excel_to_pdf', 'pdf_to_excel',
        'ppt_to_pdf', 'pdf_to_ppt', 'compress_pdf', 'split_pdf', 'merge_pdf'
    ])

    if operation == 'merge_pdf':
        uploaded_files = st.file_uploader('Unggah beberapa file PDF (minimal 2)', type=['pdf'], accept_multiple_files=True)
    else:
        uploaded_file = st.file_uploader('Unggah file input', type=['docx','pdf','xlsx','pptx'], accept_multiple_files=False)

    if operation == 'merge_pdf' and uploaded_files:
        if len(uploaded_files) < 2:
            st.warning('Minimal 2 file PDF untuk merge.')
        else:
            paths = []
            _ensure_dir('tmp/uploads')
            for f in uploaded_files:
                path = os.path.join('tmp/uploads', f.name)
                with open(path, 'wb') as out:
                    out.write(f.getbuffer())
                paths.append(path)

            output_path = os.path.join('tmp/outputs', f'merged_{int(time.time())}.pdf')
            result = merge_pdfs(paths, output_path)
            st.success('✅ Merge berhasil')
            with open(result, 'rb') as out:
                st.download_button('⬇️ Unduh hasil merge', out, file_name=os.path.basename(result), mime='application/pdf')

    elif operation != 'merge_pdf' and uploaded_file:
        _ensure_dir('tmp/uploads')
        in_path = os.path.join('tmp/uploads', uploaded_file.name)
        with open(in_path, 'wb') as out:
            out.write(uploaded_file.getbuffer())

        output_dir = 'tmp/outputs'
        _ensure_dir(output_dir)

        try:
            if operation == 'word_to_pdf':
                out_path = word_to_pdf(in_path, output_dir)
            elif operation == 'pdf_to_word':
                out_path = pdf_to_word(in_path, output_dir)
            elif operation == 'excel_to_pdf':
                out_path = excel_to_pdf(in_path, output_dir)
            elif operation == 'pdf_to_excel':
                out_path = pdf_to_excel(in_path, output_dir)
            elif operation == 'ppt_to_pdf':
                out_path = ppt_to_pdf(in_path, output_dir)
            elif operation == 'pdf_to_ppt':
                out_path = pdf_to_ppt(in_path, output_dir)
            elif operation == 'compress_pdf':
                out_path = os.path.join(output_dir, f'compressed_{os.path.basename(in_path)}')
                compress_pdf(in_path, out_path)
            elif operation == 'split_pdf':
                split_paths = split_pdf(in_path, output_dir)
                archive_path = shutil.make_archive(os.path.splitext(os.path.join(output_dir, f'split_{int(time.time())}'))[0], 'zip', output_dir)
                st.success(f'✅ Split berhasil ({len(split_paths)} halaman)')
                with open(archive_path, 'rb') as out:
                    st.download_button('⬇️ Unduh ZIP hasil split', out, file_name=os.path.basename(archive_path), mime='application/zip')
                out_path = None
            else:
                out_path = None

            if out_path:
                st.success('✅ Operasi selesai')
                with open(out_path, 'rb') as out_file:
                    st.download_button('⬇️ Unduh hasil', out_file, file_name=os.path.basename(out_path), mime='application/octet-stream')

        except Exception as e:
            st.error(f'❌ Gagal: {e}')
st.markdown("<br><br><p style='text-align: center; color: #999; font-size: 0.9em;'>🤖 Bot & Website Terintegrasi &bull; Support: SeaBank / 901067312394 (Afgani)</p>", unsafe_allow_html=True)
