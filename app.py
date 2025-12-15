import streamlit as st
from pypdf import PdfWriter
from io import BytesIO

st.set_page_config(page_title="PDF Merger", page_icon="📄")

st.title("📄 PDF Merger")
st.write("Upload multiple PDF files and merge them into a single PDF.")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Merge PDFs"):
        merger = PdfWriter()

        for pdf in uploaded_files:
            merger.append(pdf)

        output_pdf = BytesIO()
        merger.write(output_pdf)
        merger.close()
        output_pdf.seek(0)

        st.success("PDFs merged successfully!")

        st.download_button(
            label="⬇️ Download merged PDF",
            data=output_pdf,
            file_name="merged.pdf",
            mime="application/pdf"
        )