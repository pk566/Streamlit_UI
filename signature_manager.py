import os
import base64
from pathlib import Path

# Use a relative path so it works perfectly on any computer or cloud server (like Streamlit Cloud)
BASE_DIR = Path(__file__).parent
SPECIMEN_DIR = BASE_DIR / "Data" / "specimen"

# Ensure the baseline directories exist before we try to save anything to them
SPECIMEN_DIR.mkdir(parents=True, exist_ok=True)

def add_signatures_to_existing_user(person_name, base64_images):
    """
    Adds 1 or more signatures to an existing user.
    'base64_images' can be a single base64 string OR a list of base64 strings.
    """
    person_path = Path(SPECIMEN_DIR) / person_name
    # 1. Check if user does not exist
    if not person_path.exists() or not person_path.is_dir():
        return "Error: User does not exist."
    
    # 2. Standardize input: if a single string is passed, wrap it in a list
    if isinstance(base64_images, str):
        base64_images = [base64_images]
        
    if not base64_images:
        return "Error: No signatures provided."
    
    # 3. Count existing images to find the starting number
    valid_exts = {".png", ".jpg", ".jpeg", ".bmp"}
    existing_images = [f for f in person_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
    start_number = len(existing_images) + 1
    
    # 4. Save all provided images
    for i, img_str in enumerate(base64_images):
        current_number = start_number + i
        
        # Determine extension
        ext = ".png"
        if img_str.startswith("data:image"):
            header, img_str = img_str.split(",", 1)
            if "jpeg" in header or "jpg" in header:
                ext = ".jpg"
            elif "bmp" in header:
                ext = ".bmp"
        
        image_data = base64.b64decode(img_str)
        image_name = f"sign{current_number}{ext}"
        image_path = person_path / image_name
        
        with open(image_path, "wb") as f:
            f.write(image_data)
            
    return f"Successfully added {len(base64_images)} signature(s) to {person_name}"


def add_new_user(person_name, base64_images=None):
    """
    Creates a new user folder.
    - If the user folder already exists but is empty, it allows adding signatures.
    - If the user folder has signatures in it, it blocks with 'User already exists'.
    """
    person_path = Path(SPECIMEN_DIR) / person_name
    # 1. Check if user already exists AND actually has signature files in it
    if person_path.exists():
        valid_exts = {".png", ".jpg", ".jpeg", ".bmp"}
        existing_images = [f for f in person_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
        
        # Only throw error if the folder is not empty
        if len(existing_images) > 0:
            return "Error: User already exists."
        
    # 2. Create the directory (exist_ok=True prevents crash if empty folder exists)
    person_path.mkdir(parents=True, exist_ok=True)
    
    # If no images are provided, exit successfully
    if not base64_images:
        return "New user added successfully (no signatures added yet)"
        
    # 3. Standardize input: if a single string is passed, wrap it in a list
    if isinstance(base64_images, str):
        base64_images = [base64_images]
        
    # 4. Save all provided images starting from sign1
    for index, img_str in enumerate(base64_images, start=1):
        
        # Determine extension
        ext = ".png"
        if img_str.startswith("data:image"):
            header, img_str = img_str.split(",", 1)
            if "jpeg" in header or "jpg" in header:
                ext = ".jpg"
            elif "bmp" in header:
                ext = ".bmp"
                
        image_data = base64.b64decode(img_str)
        image_name = f"sign{index}{ext}"
        image_path = person_path / image_name
        
        with open(image_path, "wb") as f:
            f.write(image_data)
            
    return f"New user added successfully with {len(base64_images)} signature(s)"