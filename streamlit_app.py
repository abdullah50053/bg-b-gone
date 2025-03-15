import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
import io
import zipfile

# Register HEIC support for PIL
register_heif_opener()

def remove_bg(image: Image.Image) -> Image.Image:
    """Remove background from an image and replace it with a white background."""
    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Process image
    output_bytes = remove(img_bytes)
    output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    
    # Replace transparent background with white
    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
    final_img = Image.alpha_composite(white_bg, output_image).convert("RGB")
    
    return final_img

def main():
    st.title("Background Removal App")
    st.write("Upload images, and the backgrounds will be removed and replaced with white.")
    
    uploaded_files = st.file_uploader("Choose images...", type=["png", "jpg", "jpeg", "heic"], accept_multiple_files=True)
    
    processed_images = {}
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file).convert("RGBA")
            st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_container_width=True)
            
            with st.spinner(f"Processing {uploaded_file.name}..."):
                result_img = remove_bg(image)
                processed_images[uploaded_file.name] = result_img
            
            st.image(result_img, caption=f"Processed Image: {uploaded_file.name}", use_container_width=True)
            
            # Save output button
            img_io = io.BytesIO()
            result_img.save(img_io, format='PNG')
            img_io.seek(0)
            st.download_button(label=f"Download {uploaded_file.name}", 
                               data=img_io, 
                               file_name=f"processed_{uploaded_file.name}.png", 
                               mime="image/png")
        
        # Create a ZIP file for all processed images
        if processed_images:
            zip_io = io.BytesIO()
            with zipfile.ZipFile(zip_io, 'w') as zipf:
                for filename, img in processed_images.items():
                    img_io = io.BytesIO()
                    img.save(img_io, format='PNG')
                    img_io.seek(0)
                    zipf.writestr(f"processed_{filename}.png", img_io.getvalue())
            zip_io.seek(0)
            
            st.download_button(label="Download All Processed Images", 
                               data=zip_io, 
                               file_name="processed_images.zip", 
                               mime="application/zip")

if __name__ == "__main__":
    main()
