import streamlit as st
import pandas as pd
import os
import barcode
from barcode.writer import ImageWriter
import io

# --- CONFIG ---
st.set_page_config(page_title="CSV Barcode Scanner", layout="wide")
FILE_NAME = "barcodes.csv"

# --- INITIALIZE CSV ---
# If the file doesn't exist yet, create an empty one
if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=["Barcode"]).to_csv(FILE_NAME, index=False)

# Load existing data into session state
if 'barcode_list' not in st.session_state:
    # Read CSV and ensure barcodes are treated as strings, not math numbers
    df = pd.read_csv(FILE_NAME, dtype={"Barcode": str})
    st.session_state.barcode_list = df["Barcode"].tolist()

# --- FILE SAVING LOGIC ---
def save_to_csv():
    # Save the current session state list back to the CSV file
    df_new = pd.DataFrame({"Barcode": st.session_state.barcode_list})
    df_new.to_csv(FILE_NAME, index=False)

def handle_scan():
    new_code = st.session_state.barcode_input.strip()
    if new_code:
        # Add to top of the list so newest is first
        st.session_state.barcode_list.insert(0, new_code)
        save_to_csv()
        st.session_state.barcode_input = ""

# --- BARCODE GENERATOR ---
def generate_barcode(code_text):
    try:
        code_class = barcode.get_barcode_class('code128')
        writer_options = {'module_width': 0.3, 'module_height': 12.0, 'font_size': 10}
        barcode_obj = code_class(code_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        return buffer.getvalue()
    except Exception:
        return None

# --- UI ---
st.title("📟 CSV File Barcode Scanner")
st.write(f"Saving data automatically to: **{FILE_NAME}**")

# Input field
st.text_input(
    "👉 Scan Barcode Here:", 
    key="barcode_input", 
    on_change=handle_scan,
    placeholder="Waiting for scanner..."
)

st.divider()

# Display List
if st.session_state.barcode_list:
    # Headers
    h1, h2, h3, h4 = st.columns([0.5, 2, 3, 1])
    h1.write("**No.**")
    h2.write("**Code**")
    h3.write("**Barcode View**")
    h4.write("**Action**")
    st.divider()

    # Loop through list
    for i, code in enumerate(st.session_state.barcode_list):
        c1, c2, c3, c4 = st.columns([0.5, 2, 3, 1])
        
        with c1:
            st.write(str(len(st.session_state.barcode_list) - i)) # Reverse numbering
            
        with c2:
            st.info(code)
            
        with c3:
            img = generate_barcode(code)
            if img:
                st.image(img, width=300)
                
        with c4:
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.barcode_list.pop(i)
                save_to_csv()
                st.rerun()
        st.write("---")
        
    # Clear All Button
    if st.button("🚨 Clear Entire File", type="primary"):
        st.session_state.barcode_list = []
        save_to_csv()
        st.rerun()
else:
    st.info("The CSV file is currently empty.")
