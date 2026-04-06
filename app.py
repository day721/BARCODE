import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
import io
import base64

# Set up the page
st.set_page_config(page_title="PDT Visual Barcode Scanner", layout="wide")

st.title("📟 PDT Barcode Collector with Visuals")
st.write("Ensure your cursor is in the box below before scanning.")

# Initialize session state
if 'barcode_list' not in st.session_state:
    st.session_state.barcode_list = []

# Function to generate barcode image as a Base64 string
def generate_barcode_image(code_text):
    try:
        # Using Code128 which is standard for most PDT scans
        code_class = barcode.get_barcode_class('code128')
        # Create barcode object
        barcode_obj = code_class(code_text, writer=ImageWriter())
        
        # Save to a byte buffer
        buffer = io.BytesIO()
        barcode_obj.write(buffer)
        
        # Encode to Base64 to display in the dataframe
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None

# Function to handle the scan input
def add_barcode():
    new_code = st.session_state.barcode_input.strip()
    if new_code:
        # Add the code to the list
        st.session_state.barcode_list.append(new_code)
        # Reset input box
        st.session_state.barcode_input = ""

# --- Input Section ---
st.text_input(
    "Scan Barcode Here:", 
    key="barcode_input", 
    on_change=add_barcode,
    placeholder="Waiting for PDT scan..."
)

st.divider()

# --- List Section ---
if st.session_state.barcode_list:
    st.subheader("Inventory List")
    
    # Create the data for the table
    table_data = []
    for idx, code in enumerate(st.session_state.barcode_list):
        table_data.append({
            "No.": idx + 1,
            "Barcode Number": code,
            "Visual Barcode": generate_barcode_image(code)
        })
    
    df = pd.DataFrame(table_data)

    # Display using st.dataframe with Image Column configuration
    st.dataframe(
        df,
        column_config={
            "Visual Barcode": st.column_config.ImageColumn("Visual Barcode", width="medium"),
            "Barcode Number": st.column_config.TextColumn("Barcode Number")
        },
        hide_index=True,
        use_container_width=True
    )

    # --- Deletion Section ---
    st.write("### Manage Items")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        to_delete = st.selectbox(
            "Select item to remove:", 
            options=range(len(st.session_state.barcode_list)),
            format_func=lambda x: f"Item {x+1}: {st.session_state.barcode_list[x]}"
        )
    
    with col2:
        if st.button("🗑️ Delete Selected", use_container_width=True):
            st.session_state.barcode_list.pop(to_delete)
            st.rerun()

    if st.button("Clear Full List"):
        st.session_state.barcode_list = []
        st.rerun()
else:
    st.info("The list is currently empty. Start scanning!")
