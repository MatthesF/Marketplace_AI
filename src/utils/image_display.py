import streamlit as st
from PIL import Image

def display_images_with_remove_option(cached_images):
    st.subheader("Uploaded Images")
    
    cols = 3  # Number of columns to display images in a grid

    if st.session_state.recommendation:
        st.write(st.session_state.recommendation)

    for i in range(0, len(cached_images), cols):
        cols_layout = st.columns(cols)
        for j in range(cols):
            if i + j < len(cached_images):
                file_index = i + j
                with cols_layout[j]:
                    # Show processed image if available, otherwise show original
                    display_image = (st.session_state.processed_images[file_index] 
                                    if st.session_state.processed_images 
                                    and st.session_state.processed_images[file_index] is not None 
                                    else cached_images[file_index])
                    st.image(display_image, use_column_width=True, caption=st.session_state.uploaded_files[file_index].name)

                    # Remove button to delete the file from session state
                    if st.button(f"Remove: {st.session_state.uploaded_files[file_index].name}", key=f"remove_{file_index}"):
                        # Get the file_id of the file to remove
                        file_id_to_remove = st.session_state.uploaded_files[file_index].file_id
                        
                        # Remove the file from uploaded_files
                        st.session_state.uploaded_files = [
                            f for f in st.session_state.uploaded_files 
                            if f.file_id != file_id_to_remove
                        ]
                        
                        # Remove the specific index from processed_images
                        if len(st.session_state.processed_images) > file_index:
                            st.session_state.processed_images.pop(file_index)
                        
                        # Increment the uploader key
                        st.session_state.uploader_key += 1
                        
                        # Rerun the app
                        st.rerun()
