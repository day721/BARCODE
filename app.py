import streamlit as st
import barcode
from barcode.writer import ImageWriter
import io
import base64

# Page config
st.set_page_config(page_title="Big Barcode List", layout="wide")

st.title("📟 Large Barcode Scanner List")

# Initialize session state
if 'barcode_list' not in st.session_state:
    st.session_state.barcode_list = []

# Function to generate a BIG barcode image
def generate_big_barcode(code_text):
    try:
        code_class = barcode.get_barcode_class('code128')
        
        # High module_width and module_height for screen scanning
        writer_options = {
            'module_width': 0.6,    # Thickness of bars
            'module_height': 25.0,  # Height of bars
            'font_size': 12,        # Text size below
            'text_distance': 5,
            'quiet_zone': 6.0       # White space around for scanner focus
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
    "👉 Click here & Scan with PDT:", 
    key="barcode_input", 
    on_change=add_barcode,
    placeholder="Waiting for input..."
)

st.divider()

# --- Custom Big List View ---
if st.session_state.barcode_list:
    st.subheader("📋 Scanned Barcodes (Scannable from Screen)")
    
    # Header row
    h1, h2, h3, h4 = st.columns([0.5, 1.5, 4, 1])
    h1.write("**No.**")
    h2.write("**Barcode Number**")
    h3.write("**Scan Directly Below**")
    h4.write("**Action**")
    st.divider()

    # Loop through the list backwards (newest at top)
    for i in range(len(st.session_state.barcode_list) - 1, -1, -1):
        code = st.session_state.barcode_list[i]
        
        # Create columns for each "row"
        col1, col2, col3, col4 = st.columns([0.5, 1.5, 4, 1])
        
        with col1:
            st.write(f"#{i+1}")
        
        with col2:
            st.code(code, language=None) # Code block makes it easy to copy if needed
            
        with col3:
            img_bytes = generate_big_barcode(code)
            if img_bytes:
                # Displaying the barcode very large
                st.image(img_bytes, use_container_width=True)
        
        with col4:
            if st.button("🗑️ Delete", key=f"del_{i}"):
                st.session_state.barcode_list.pop(i)
                st.rerun()
        
        st.divider()

    if st.button("🚨 Clear All Barcodes"):
        st.session_state.barcode_list = []
        st.rerun()
else:
    st.info("The list is empty. Scan a barcode to start.")
