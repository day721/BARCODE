import streamlit as st
import barcode
from barcode.writer import ImageWriter
import io

# Page config
st.set_page_config(page_title="Standard Barcode List", layout="wide")

st.title("📟 Barcode Collector (Standard Size)")

# Initialize session state
if 'barcode_list' not in st.session_state:
    st.session_state.barcode_list = []

def generate_standard_barcode(code_text):
    try:
        code_class = barcode.get_barcode_class('code128')
        
        # "Standard" settings for screen scannability without being huge
        writer_options = {
            'module_width': 0.3,    # Standard thickness
            'module_height': 12.0,  # Shorter bars
            'font_size': 10,
            'text_distance': 4,
            'quiet_zone': 2.0       
        }

        barcode_obj = code_class(code_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        return buffer.getvalue()
    except Exception:
        return None

def add_barcode():
    new_code = st.session_state.barcode_input.strip()
    if new_code:
        st.session_state.barcode_list.append(new_code)
        st.session_state.barcode_input = ""

# --- Input Section ---
st.text_input(
    "👉 Click & Scan:", 
    key="barcode_input", 
    on_change=add_barcode,
    placeholder="PDT input here..."
)

st.divider()

# --- List Section ---
if st.session_state.barcode_list:
    # Column headers
    h1, h2, h3, h4 = st.columns([0.5, 2, 3, 1])
    h1.write("**No.**")
    h2.write("**Code**")
    h3.write("**Barcode View**")
    h4.write("**Action**")
    st.divider()

    # Show newest first
    for i in range(len(st.session_state.barcode_list) - 1, -1, -1):
        code = st.session_state.barcode_list[i]
        col1, col2, col3, col4 = st.columns([0.5, 2, 3, 1])
        
        with col1:
            st.write(f"{i+1}")
        
        with col2:
            st.info(code) # Displays number in a nice blue box
            
        with col3:
            img_bytes = generate_standard_barcode(code)
            if img_bytes:
                # 'width=300' keeps it at a standard, readable size
                st.image(img_bytes, width=300)
        
        with col4:
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.barcode_list.pop(i)
                st.rerun()
        
        st.write("---") # Thin separator between rows

    if st.button("Clear All"):
        st.session_state.barcode_list = []
        st.rerun()
else:
    st.info("No barcodes in list.")
