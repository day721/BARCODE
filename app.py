import streamlit as st
import pandas as pd
import os
import barcode
from barcode.writer import ImageWriter
import io
import time

# --- CONFIG ---
st.set_page_config(page_title="Global Sync Barcode Scanner", layout="wide")
FILE_NAME = "barcodes.csv"

# --- GLOBAL SHARED STORAGE ---
# This allows different users/devices to access the same data in memory
@st.cache_resource
def get_global_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME, dtype={"Barcode": str})
        return {"list": df["Barcode"].tolist(), "last_update": time.time()}
    return {"list": [], "last_update": time.time()}

shared_state = get_global_data()

def sync_to_disk():
    """Saves the global memory state to the CSV file."""
    df = pd.DataFrame({"Barcode": shared_state["list"]})
    df.to_csv(FILE_NAME, index=False)
    shared_state["last_update"] = time.time()

# --- BARCODE GENERATOR ---
@st.cache_data
def generate_barcode(code_text):
    try:
        code_class = barcode.get_barcode_class('code128')
        writer_options = {'module_width': 0.3, 'module_height': 12.0, 'font_size': 10}
        barcode_obj = code_class(code_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        return buffer.getvalue()
    except:
        return None

# --- UI LOGIC ---
st.title("📟 Real-Time Shared Barcode Scanner")
st.caption("Syncing across all devices via GitHub/Streamlit Cloud")

def handle_scan():
    val = st.session_state.barcode_input.strip()
    if val:
        # Update shared memory
        shared_state["list"].insert(0, val)
        sync_to_disk()
        st.session_state.barcode_input = ""

# Input field - Outside the fragment so it doesn't lose focus
st.text_input(
    "👉 Scan Barcode Here:", 
    key="barcode_input", 
    on_change=handle_scan,
    placeholder="Waiting for scanner..."
)

st.divider()

# --- THE AUTO-REFRESH FRAGMENT ---
# This part runs every 2 seconds on every device automatically
@st.fragment(run_every="2s")
def display_list_realtime():
    # We use a local session state timestamp to check if we need to redraw
    if "local_last_update" not in st.session_state:
        st.session_state.local_last_update = 0

    # If the global data has changed since our last fragment run, this will update
    current_data = shared_state["list"]
    
    if not current_data:
        st.info("No barcodes scanned yet.")
        return

    # Table Header
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
            img = generate_barcode(code)
            if img:
                st.image(img, width=250)
        with c4:
            # Unique key includes the timestamp to prevent UI lag/conflicts
            if st.button("🗑️", key=f"del_{i}_{shared_state['last_update']}"):
                shared_state["list"].pop(i)
                sync_to_disk()
                st.rerun()
        st.write("---")

    if st.button("🚨 Clear All Data", type="primary", use_container_width=True):
        shared_state["list"] = []
        sync_to_disk()
        st.rerun()

# Execute the auto-updating section
display_list_realtime()
