import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(page_title="PDT Barcode Scanner", layout="centered")

st.title("📟 PDT Barcode Collector")
st.write("Click the input box and start scanning with your PDT.")

# Initialize session state for the barcode list
if 'barcode_list' not in st.session_state:
    st.session_state.barcode_list = []

# Function to add barcode
def add_barcode():
    new_code = st.session_state.barcode_input.strip()
    if new_code:
        # Avoid duplicates if desired, or just append
        st.session_state.barcode_list.append(new_code)
        # Clear the input for the next scan
        st.session_state.barcode_input = ""

# --- Input Section ---
# The 'on_change' trigger handles the 'Enter' key sent by most PDT scanners
st.text_input(
    "Scan Barcode Here:", 
    key="barcode_input", 
    on_change=add_barcode,
    placeholder="Waiting for scan..."
)

st.divider()

# --- List Section ---
st.subheader("Scanned Barcodes")

if st.session_state.barcode_list:
    # Create a list for display with index numbers
    data = {
        "No.": range(1, len(st.session_state.barcode_list) + 1),
        "Barcode": st.session_state.barcode_list
    }
    df = pd.DataFrame(data)
    
    # Display the table
    st.table(df)

    # --- Deletion Section ---
    st.write("### Manage List")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        to_delete = st.selectbox("Select Barcode to Remove", 
                                 options=range(len(st.session_state.barcode_list)),
                                 format_func=lambda x: f"Item {x+1}: {st.session_state.barcode_list[x]}")
    
    with col2:
        if st.button("🗑️ Delete", use_container_width=True):
            st.session_state.barcode_list.pop(to_delete)
            st.rerun()

    # Clear All Button
    if st.button("Clear All List"):
        st.session_state.barcode_list = []
        st.rerun()
else:
    st.info("No barcodes scanned yet.")

# Optional: Download as CSV
if st.session_state.barcode_list:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download List as CSV", data=csv, file_name="barcodes.csv", mime="text/csv")
