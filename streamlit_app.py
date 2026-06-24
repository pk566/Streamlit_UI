import streamlit as st
import base64
from pathlib import Path

# Import the functions from the separate signature_manager file
from signature_manager import SPECIMEN_DIR, add_signatures_to_existing_user, add_new_user

# Helper to convert Streamlit files to base64 Data URIs
def file_to_base64_uri(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.getvalue()
    b64_str = base64.b64encode(bytes_data).decode("utf-8")
    return f"data:{uploaded_file.type};base64,{b64_str}"

# Initialize session state to track the number of user forms being filled out
if "user_rows" not in st.session_state:
    st.session_state.user_rows = 1

# ----------------------------------------------------
# STREAMLIT USER INTERFACE
# ----------------------------------------------------
st.set_page_config(page_title="Signature Specimen Manager", layout="wide")
st.title("Signature Specimen Manager")

# Create two columns: Left for actions, Right to monitor the directory
col_actions, col_monitor = st.columns([2, 1])

with col_actions:
    st.subheader("Manage Specimens")
    
    # Create tabs for the two tasks
    tab1, tab2 = st.tabs(["Add New User(s)", "Add Signatures to Existing User"])
    
    # --- Tab 1: Add New User(s) ---
    with tab1:
        st.write("### Create New User Folders")
        
        # A dictionary to collect name -> list of base64 images
        batch_users_data = {}
        
        # Render dynamic rows for users
        for i in range(st.session_state.user_rows):
            st.markdown(f"#### User {i+1}")
            col_name, col_files = st.columns([1, 2])
            
            with col_name:
                u_name = st.text_input(
                    f"User Name", 
                    placeholder="e.g., Person59", 
                    key=f"user_name_{i}"
                )
            with col_files:
                u_files = st.file_uploader(
                    f"Upload signatures (Optional)", 
                    type=["png", "jpg", "jpeg", "bmp"], 
                    accept_multiple_files=True,
                    key=f"user_files_{i}"
                )
            
            if u_name.strip():
                # Convert files to base64 list
                b64_list = [file_to_base64_uri(f) for f in u_files] if u_files else []
                batch_users_data[u_name.strip()] = b64_list
                
            st.markdown("---")
        
        # Control Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("Add Another User"):
                st.session_state.user_rows += 1
                st.rerun()
        with col_btn2:
            if st.button("Clear Form Rows"):
                st.session_state.user_rows = 1
                st.rerun()
        with col_btn3:
            if st.button("Create All Users", type="primary"):
                if not batch_users_data:
                    st.error("Please fill in at least one user name.")
                else:
                    # Loop through the dictionary and call the function for each user
                    all_success = True
                    for u_name, images in batch_users_data.items():
                        result = add_new_user(u_name, images)
                        
                        if "Error" in result:
                            st.error(f"{u_name}: {result}")
                            all_success = False
                        else:
                            st.success(f"{u_name}: {result}")
                            
                    # If everything went well, reset the form
                    if all_success:
                        st.session_state.user_rows = 1
                        st.rerun()

    # --- Tab 2: Add Signatures to Existing User ---
    with tab2:
        st.write("### Add Signatures to an Existing User")
        
        # List folder names for dropdown selection
        specimen_path_obj = Path(SPECIMEN_DIR)
        existing_users = []
        if specimen_path_obj.exists():
            existing_users = sorted([p.name for p in specimen_path_obj.iterdir() if p.is_dir()])
            
        selected_user = st.selectbox("Select Existing User", ["-- Select User --"] + existing_users)
        
        # Upload one or more files
        uploaded_existing_files = st.file_uploader(
            "Upload 1 or more signatures", 
            type=["png", "jpg", "jpeg", "bmp"], 
            accept_multiple_files=True,
            key="existing_user_uploader"
        )
        
        if st.button("Add Signature(s)", type="primary"):
            if selected_user == "-- Select User --":
                st.error("Please select a user.")
            elif not uploaded_existing_files:
                st.error("Please upload at least one signature image.")
            else:
                # Convert uploaded files to base64 list
                b64_list = [file_to_base64_uri(f) for f in uploaded_existing_files]
                
                # Execute Function
                result = add_signatures_to_existing_user(selected_user, b64_list)
                
                # Display Results
                if "Error" in result:
                    st.error(result)
                else:
                    st.success(result)
                    st.rerun()

# --- Right column: Folder Monitor ---
with col_monitor:
    st.subheader("Specimen Folders")
    
    specimen_path_obj = Path(SPECIMEN_DIR)
    if not specimen_path_obj.exists():
        st.error("Specimen directory not found!")
    else:
        folders = sorted([p for p in specimen_path_obj.iterdir() if p.is_dir()], key=lambda p: p.name)
        
        if not folders:
            st.info("No folders inside specimen directory.")
        else:
            for folder in folders:
                # Find all images inside the folder
                valid_exts = {".png", ".jpg", ".jpeg", ".bmp"}
                images = sorted([f.name for f in folder.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])
                
                # Render an expander showing the files in each folder
                with st.expander(f"{folder.name} ({len(images)} images)"):
                    if not images:
                        st.write("*(No images)*")
                    for img in images:
                        st.write(f"- {img}")