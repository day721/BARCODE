import streamlit as st
import pandas as pd
import os
import barcode
from barcode.writer import ImageWriter
import io
import time
from fpdf import FPDF

# --- CONFIG ---
st.set_page_config(page_title="Global Sync Barcode Scanner", layout="wide")
FILE_NAME = "barcodes.csv"

# --- GLOBAL SHARED STORAGE ---
@st.cache_resource
def get_global_data():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_csv(FILE_NAME, dtype={"Barcode": str})
            return {"list": df["Barcode"].tolist(), "last_update": time.time()}
        except:
            return {"list": [], "last_update": time.time()}
    return {"list": [], "last_update": time.time()}

shared_state = get_global_data()

def sync_to_disk():
    df = pd.DataFrame({"Barcode": shared_state["list"]})
    df.to_csv(FILE_NAME, index=False)
    shared_state["last_update"] = time.time()

# --- BARCODE GENERATOR ---
@st.cache_data
def generate_barcode_image(code_text):
    """Returns the barcode as raw bytes (PNG)."""
    try:
        code_class = barcode.get_barcode_class('code128')
        writer_options = {'module_width': 0.3, 'module_height': 12.0, 'font_size': 10}
        barcode_obj = code_class(code_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        return buffer.getvalue()
    except:
        return None

# --- PDF EXPORT LOGIC ---
def create_pdf(barcode_list):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, txt="Scanned Barcode Report", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Helvetica", size=12)
        
        for i, code in enumerate(barcode_list):
            # Text Label
            pdf.cell(0, 10, txt=f"Item {len(barcode_list)-i}: {code}", ln=True)
            
            # Generate image bytes
            img_bytes = generate_barcode_image(code)
            if img_bytes:
                # FPDF2 can accept io.BytesIO for images
                img_io = io.BytesIO(img_bytes)
                pdf.image(img_io, x=10, w=100)
                pdf.ln(5)
        
        # CRITICAL FIX: Explicitly cast output to bytes
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        return None

# --- UI LOGIC ---
st.title("📟 Real-Time Shared Barcode Scanner")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Actions")
    if shared_state["list"]:
        # 1. Generate PDF Bytes
        pdf_data = create_pdf(shared_state["list"])
        
        # 2. Only show button if data exists and is not None
        if pdf_data:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name="barcodes_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # CSV Download
        df_download = pd.DataFrame({"Barcode": shared_state["list"]})
        csv_data = df_download.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name="barcodes.csv",
            mime="text/csv",
            use_container_width=True
        )

def handle_scan():
    val = st.session_state.barcode_input.strip()
    if val:
        shared_state["list"].insert(0, val)
        sync_to_disk()
        st.session_state.barcode_input = ""

st.text_input(
    "👉 Scan Barcode Here:", 
    key="barcode_input", 
    on_change=handle_scan,
    placeholder="Waiting for scanner..."
)

st.divider()

# --- THE AUTO-REFRESH FRAGMENT ---
@st.fragment(run_every="2s")
def display_list_realtime():
    current_data = shared_state["list"]
    
    if not current_data:
        st.info("No barcodes scanned yet.")
        return

    h1, h2, h3, h4 = st.columns([0.5, 2, 3, 1])
    h1.write("**No.**")
    h2.write("**Code**")
    h3.write("**Barcode View**")
    h4.write("**Action**")
    st.write("---")

    for i, code in enumerate(current_data):
        c1, c2, c3, c4 = st.columns([0.5, 2, 3, 1])
        with c1:
            st.write(len(current_data) - i)
        with c2:
            st.code(code, language=None)
        with c3:
            img_bytes = generate_barcode_image(code)
            if img_bytes:
                st.image(img_bytes, width=250)
        with c4:
            if st.button("🗑️", key=f"del_{i}_{shared_state['last_update']}"):
                shared_state["list"].pop(i)
                sync_to_disk()
                st.rerun()
        st.write("---")

    if st.button("🚨 Clear All Data", type="primary", use_container_width=True):
        shared_state["list"] = []
        sync_to_disk()
        st.rerun()

display_list_realtime()
