import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from streamlit_sortables import sort_items
from io import BytesIO
import re

st.set_page_config("Advanced PDF Merger", "📄", layout="wide")
st.title("📄 Advanced PDF Merger")

def parse_pages(page_text, max_page):
    pages = set()
    for part in page_text.split(","):
        if "-" in part:
            start, end = part.split("-")
            pages.update(range(int(start)-1, int(end)))
        elif part.strip().isdigit():
            pages.add(int(part)-1)
    return sorted(p for p in pages if 0 <= p < max_page)

uploaded = st.file_uploader(
    "Upload PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded:
    if "pdfs" not in st.session_state:
        st.session_state.pdfs = {}

        for f in uploaded:
            st.session_state.pdfs[f.name] = {
                "bytes": f.read(),
                "name": f.name,
                "pages": "",
                "password": ""
            }

if "pdfs" in st.session_state and st.session_state.pdfs:
    st.subheader("↔️ Reorder PDFs")
    pdf_order = sort_items(list(st.session_state.pdfs.keys()))

    for key in list(st.session_state.pdfs.keys()):
        if key not in pdf_order:
            del st.session_state.pdfs[key]

    new_pdfs = {}
    for name in pdf_order:
        new_pdfs[name] = st.session_state.pdfs[name]
    st.session_state.pdfs = new_pdfs

    st.subheader("📑 PDF Settings & Preview")

    for key, pdf in list(st.session_state.pdfs.items()):
        with st.expander(pdf["name"], expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                pdf["name"] = st.text_input("Rename", pdf["name"], key=f"rename_{key}")
                pdf["pages"] = st.text_input(
                    "Pages to include (e.g. 1-3,5) — blank = all",
                    pdf["pages"],
                    key=f"pages_{key}"
                )
                pdf["password"] = st.text_input(
                    "Password (if protected)",
                    pdf["password"],
                    type="password",
                    key=f"pwd_{key}"
                )

                if st.button("🗑️ Delete PDF", key=f"del_{key}"):
                    del st.session_state.pdfs[key]
                    st.rerun()

            with col2:
                images = convert_from_bytes(pdf["bytes"])
                for img in images:
                    st.image(img, use_container_width=True)

    st.subheader("📄 Page-Level Reordering (Optional)")
    selected_pdf = st.selectbox("Select PDF", list(st.session_state.pdfs.keys()))

    reader = PdfReader(BytesIO(st.session_state.pdfs[selected_pdf]["bytes"]))
    page_labels = [f"Page {i+1}" for i in range(len(reader.pages))]
    ordered_pages = sort_items(page_labels)

    if st.button("📎 Merge PDFs"):
        merger = PdfWriter()

        for pdf in st.session_state.pdfs.values():
            reader = PdfReader(BytesIO(pdf["bytes"]))
            if pdf["password"]:
                reader.decrypt(pdf["password"])

            if pdf["pages"]:
                pages = parse_pages(pdf["pages"], len(reader.pages))
            else:
                pages = range(len(reader.pages))

            for i in pages:
                merger.add_page(reader.pages[i])

        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)

        st.success("✅ PDFs merged successfully")

        st.download_button(
            "⬇️ Download Merged PDF",
            data=output,
            file_name="merged.pdf",
            mime="application/pdf"
        )