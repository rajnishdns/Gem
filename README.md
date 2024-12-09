# Gem - Multi-Modal AI Assistant

A sophisticated Streamlit-based interface for interacting with Google's LearnLM experimental model, supporting images and videos.

## Features

- 💎 Clean, modern interface with proper styling
- 🖼️ Support for image uploads (PNG, JPG, JPEG)
- 🎥 Support for video uploads (MP4, AVI, MOV)
- 💬 Chat-style interface with message history
- 🎨 Beautiful message formatting
- 📱 Responsive design
- ⚡ Real-time responses
- 🔄 Clear chat functionality

## Prerequisites

1. Install the required system packages:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv libmagic1
```

2. Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Google API key:
   - Create a `.streamlit/secrets.toml` file:
     ```bash
     mkdir -p .streamlit
     echo 'GOOGLE_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml
     ```
   - Or set it as an environment variable:
     ```bash
     export GOOGLE_API_KEY="your-api-key-here"
     ```

## Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. Upload an image or video using the sidebar
2. Ask questions about the uploaded file in the chat interface
3. View the AI's responses in a clean, formatted way
4. Clear the chat history using the sidebar button when needed

## Supported File Types

- Images: PNG, JPG, JPEG
- Videos: MP4, AVI, MOV

## Notes

- The LearnLM experimental model is used for processing both images and videos
- Maximum file size: 2GB
- Video processing may take longer due to the size and complexity
- The model can understand and respond to questions about both visual content and context
