import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import magic
import base64
import httpx
from config import *

# Configure the page
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E3F2FD;
    }
    .assistant-message {
        background-color: #F5F5F5;
    }
    .media-preview {
        max-width: 300px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini API
def initialize_genai():
    try:
        # Try to get API key from different sources
        api_key = GOOGLE_API_KEY
        if api_key == "YOUR-API-KEY-HERE":
            st.error("Please set your Google API key in config.py")
            st.stop()
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.error(f"Error initializing Gemini API: {str(e)}")
        st.stop()

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None, None
    
    try:
        file_type = magic.from_buffer(uploaded_file.getvalue(), mime=True)
        content = uploaded_file.getvalue()
        
        if file_type.startswith('image/'):
            return {
                'mime_type': file_type,
                'data': base64.b64encode(content).decode('utf-8')
            }, file_type
        elif file_type.startswith('video/'):
            # For videos, return the content directly
            return {
                'mime_type': file_type,
                'data': base64.b64encode(content).decode('utf-8')
            }, file_type
        elif file_type.startswith(('text/', 'application/pdf')):
            # For text files and PDFs, return the content as base64
            return {
                'mime_type': file_type,
                'data': base64.b64encode(content).decode('utf-8')
            }, file_type
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None, None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None, None

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'current_file_type' not in st.session_state:
    st.session_state.current_file_type = None
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = True

# Sidebar
with st.sidebar:
    st.title(f"{PAGE_ICON} Gem Settings")
    st.markdown("---")
    
    # File upload section
    st.subheader("Upload Files")
    uploaded_file = st.file_uploader(
        "Choose a file to analyze",
        type=ALL_SUPPORTED_TYPES,
        help=f"""Supported formats:
        - Images: {', '.join(SUPPORTED_IMAGE_TYPES)}
        - Videos: {', '.join(SUPPORTED_VIDEO_TYPES)}
        - Documents: {', '.join(SUPPORTED_TEXT_TYPES)}"""
    )
    
    if uploaded_file:
        # Check file size
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
        if file_size > MAX_FILE_SIZE:
            st.error(f"File size ({file_size:.1f}MB) exceeds the maximum limit of {MAX_FILE_SIZE}MB")
        else:
            processed_file, file_type = process_uploaded_file(uploaded_file)
            if processed_file:
                st.session_state.current_file = processed_file
                st.session_state.current_file_type = file_type
                st.session_state.show_preview = True  # Show preview for newly uploaded file
                st.success(f"File uploaded successfully! Type: {file_type}")
                
                # Show file preview in sidebar
                st.subheader("File Preview")
                if file_type.startswith('image/'):
                    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                elif file_type.startswith('video/'):
                    st.video(uploaded_file)
                elif file_type.startswith(('text/', 'application/pdf')):
                    if file_type == 'application/pdf':
                        st.markdown("PDF file uploaded successfully")
                    else:
                        # Show preview of text content
                        text_content = uploaded_file.getvalue().decode('utf-8')
                        st.text_area("File Content Preview", text_content[:500] + ("..." if len(text_content) > 500 else ""), height=150)
    
    # Clear chat button
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.session_state.current_file = None
        st.session_state.current_file_type = None
        st.session_state.show_preview = True
        st.rerun()

# Main content
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("Ask questions about uploaded files using Google's LearnLM model")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("What would you like to ask about the uploaded file?"):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    try:
        model = initialize_genai()
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = None
                # Prepare the prompt with the file if available
                if st.session_state.current_file:
                    # Create a prompt that includes file content for text files
                    if st.session_state.current_file_type.startswith(('text/', 'application/pdf')):
                        try:
                            file_content = base64.b64decode(st.session_state.current_file['data']).decode('utf-8')
                            text_prompt = f"Here's the content of the file:\n\n{file_content}\n\nUser's question: {prompt}"
                            response = model.generate_content(text_prompt)
                        except Exception as e:
                            st.error(f"Error processing text file: {str(e)}")
                    else:
                        # For images and videos, use the standard approach
                        response = model.generate_content([
                            st.session_state.current_file,
                            prompt
                        ])
                else:
                    response = model.generate_content(prompt)
                
                # Display the response if we got one
                if response:
                    st.markdown(response.text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.text
                    })
                    
                    # Disable preview after first interaction
                    st.session_state.show_preview = False
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using Google's LearnLM Experimental Model | "
    "Supports images, videos, and text files"
)
