import streamlit as st
import barcode
from barcode.writer import ImageWriter
import io
import json
import base64
from github import Github  # You'll need to add PyGithub to requirements.txt

# --- CONFIG ---
st.set_page_config(page_title="GitHub Synced Scanner", layout="wide")

# --- GITHUB SYNC LOGIC ---
# Securely get your GitHub Token from Streamlit Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "your-username/your-repo-name" # Change this to your repo
FILE_PATH = "data.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def load_data():
    try:
        contents = repo.get_contents(FILE_PATH)
        return json.loads(contents.decoded_content.decode()), contents.sha
    except:
        return [], None

def save_data(new_list):
    data_str = json.dumps(new_list, indent=4)
    _, sha = load_data()
    if sha:
        repo.update_file(FILE_PATH, "Update barcode list", data_str, sha)
    else:
        repo.create_file(FILE_PATH, "Create barcode list", data_str)

# --- BARCODE GENERATOR ---
def generate_barcode(code_text):
    try:
        code_class = barcode.get_barcode_class('code128')
        writer_options = {'module_width': 0.3, 'module_height': 12.0, 'font_size': 10}
        barcode_obj = code_class(code_text, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        return buffer.getvalue()
    except: return None

# --- APP UI ---
st.title("📟 GitHub Synced Barcodes")
st.info("Scanning here updates the JSON file in your GitHub repo for all devices to see.")

# Load current data from GitHub
current_list, file_sha = load_data()

def handle_scan():
    code = st.session_state.barcode_input.strip()
    if code:
        current_list.append(code)
        save_data(current_list)
        st.session_state.barcode_input = ""

st.text_input("👉 Scan Barcode:", key="barcode_input", on_change=handle_scan)

st.divider()

if current_list:
    # Header
    col_no, col_txt, col_img, col_btn = st.columns([0.5, 2, 3, 1])
    col_no.write("**No.**")
    col_txt.write("**Code**")
    col_img.write("**Barcode View**")
    
    # Show items (Newest first)
    for i in range(len(current_list) - 1, -1, -1):
        c1, c2, c3, c4 = st.columns([0.5, 2, 3, 1])
        with c1: st.write(i + 1)
        with c2: st.info(current_list[i])
        with c3:
            img = generate_barcode(current_list[i])
            if img: st.image(img, width=300)
        with c4:
            if st.button("Delete", key=f"del_{i}"):
                current_list.pop(i)
                save_data(current_list)
                st.rerun()
        st.write("---")
else:
    st.write("No data found in GitHub JSON.")
