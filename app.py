import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
import io
import base64

# Set up the page for a wider view
st.set_page_config(page_title="Large Barcode Scanner", layout="wide")

st.title("📟 High-Visibility PDT Collector")

# Initialize session state
if 'barcode_list' not in st.session_state:
    st.session_state.barcode_list = []
if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = None

def generate_barcode_image(code_text, is_preview=False):
    try:
        # Code128 is versatile. 
        # For UPC-A (like your photo), you can use barcode.get('upca', ...)
        code_class = barcode.get_barcode_class('code128')
        
        # Adjusting the thickness for scannability
        # module_width: width of the thinnest bar
        # module_height: height of the bars
        writer_options = {
            'module_width': 0.4, 
            'module_height': 20.0, 
            'font_size': 10,
            'text_distance': 5
        } if not is_preview else {
            'module_width': 0.8, # Double thickness for preview
            'module_height': 30.0, 
            'font_size': 15,
            'text_distance': 8
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
        st.session_state.last_scanned = new_code
        st.session_state.barcode_input = ""

# --- Layout: Input and Preview ---
col_in, col_pre = st.columns([1, 1])

with col_in:
    st.subheader("1. Scan Input")
    st.text_input(
        "Click here & Scan:", 
        key="barcode_input", 
        on_change=add_barcode,
        placeholder="Waiting for scan..."
    )

with col_pre:
    st.subheader("2. Last Scanned (Big View)")
    if st.session_state.last_scanned:
        img_bytes = generate_barcode_image(st.session_state.last_scanned, is_preview=True)
        if img_bytes:
            st.image(img_bytes, caption=f"Current: {st.session_state.last_scanned}", use_container_width=True)
    else:
        st.info("Scan something to see the preview.")

st.divider()

# --- List Section ---
if st.session_state.barcode_list:
    st.subheader("3. Scanned History")
    
    # Prepare data for the table
    table_data = []
    for idx, code in enumerate(st.session_state.barcode_list):
        img_bytes = generate_barcode_image(code)
        # Convert to Base64 for the dataframe column
        b64 = base64.b64encode(img_bytes).decode()
        table_data.append({
            "No.": idx + 1,
            "Number": code,
            "Barcode View": f"data:image/png;base64,{b64}"
        })
    
    df = pd.DataFrame(table_data)

    # Displaying the list with a "Large" image configuration
    st.dataframe(
        df,
        column_config={
            "Barcode View": st.column_config.ImageColumn("Barcode View", width="large"),
            "Number": st.column_config.TextColumn("Number", width="medium")
        },
        hide_index=True,
        use_container_width=True
    )

    # --- Deletion ---
    with st.expander("Manage/Delete Barcodes"):
        to_delete = st.selectbox(
            "Select to remove:", 
            options=range(len(st.session_state.barcode_list)),
            format_func=lambda x: f"Item {x+1}: {st.session_state.barcode_list[x]}"
        )
        if st.button("🗑️ Delete Selected"):
            st.session_state.barcode_list.pop(to_delete)
            st.rerun()
        
        if st.button("🚨 Clear All"):
            st.session_state.barcode_list = []
            st.rerun()
else:
    st.write("Scan a barcode to populate the list.")
