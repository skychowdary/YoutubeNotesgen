# Importing necessary libraries
import streamlit as st  
import os  
import re  
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled  
from docx import Document  
from g4f.client import Client  
from dotenv import load_dotenv 
from io import BytesIO  

# Initialize the GPT-4 Free client
client = Client()

# Load environment variables
load_dotenv()

# Set the logo and page configuration
logo_path = 'https://vectorseek.com/wp-content/uploads/2023/06/Youtube-Black-icon-Vector.jpg'
st.set_page_config(page_title='Youtube Notesgen', page_icon=logo_path)

# Prompt for video summarizer
prompt = """You are YouTube NotesGen, an AI-powered note-taking assistant. You have watched the video based on the provided transcript and understand its content. Your goal is to create concise, comprehensive, and easy-to-understand notes summarizing the key points of the video. Imagine you are summarizing the video for someone who hasn't watched it. Your objective is to deliver top-notch notes, rated 10/10 for clarity, coherence, and informativeness. Utilize the provided transcript to craft the best possible notes, ensuring they are insightful, well-structured, and easily digestible. """

# Function to extract transcript details from YouTube videos
def extract_transcript_details(youtube_video_url):
    video_id = None
    try:
        # Extract the video ID from a YouTube URL using regex
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_video_url)
        video_id = match.group(1) if match else None
        if not video_id:
            raise ValueError("Video ID could not be extracted from the URL.")

        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join(i["text"] for i in transcript)
        return transcript_text

    except TranscriptsDisabled:
        st.error(f"Transcripts are disabled for this video: {youtube_video_url}")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred while retrieving the transcript for video ID {video_id}: {e}")
    return None

# Function to generate notes using GPT-4 Free
def generate_g4f_notes(transcript_text, prompt):
    response = client.chat.completions.create(
        model="gpt-4", # Assuming gpt-3.5-turbo model, may change based on your `g4f` setup
        messages=[{"role": "user", "content": prompt + transcript_text}],
    )
    return response.choices[0].message.content

# Custom CSS for enhanced styling
custom_css = """
<style>
    body {
        background-color: #f0f2f6;
        font-family: Arial, sans-serif;
    }
    .stApp {
        max-width: 800px;
        margin: auto;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    .stTextInput>label {
        color: #333333;
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #000000;
    }
    .stMarkdown>h1 {
        color: #333333;
        text-align: center;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Image and UI components layout
col1, col2 = st.columns([0.3, 1.8])
col1.image('http://res.cloudinary.com/dwmwpmrpo/image/upload/v1711370473/vmmhcrekf6cenvimqrss.png', width=300)

# UI layout
with st.container():
    # Form
    with st.form("my_form"):
        youtube_link = st.text_input("Enter YouTube Video Link:")
        submitted = st.form_submit_button("Start")

st.markdown("###### Created by: [Sai kiran yadagini](https://www.linkedin.com/in/sai-kiran-yadagini/)")


if submitted:
    with st.spinner('Please wait...'):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            notes = generate_g4f_notes(transcript_text, prompt) 
            if notes:
                st.markdown("## Detailed Notes:") 
                st.write(notes)

                # Create a Word document
                doc = Document()
                doc.add_heading('Video Notes', 0)  
                doc.add_paragraph(notes)

                # Save the document to a BytesIO object
                buf = BytesIO()
                doc.save(buf)
                buf.seek(0)

                # Use Streamlit's download button to offer the Word document for download
                btn = st.download_button(
                    label="Download Word",
                    data=buf,
                    file_name="video_notes.docx" 
                )

            else:
                st.error("Failed to generate the notes.") 
        else:
            st.error("Could not fetch the transcript or generate notes.")  

# Hide unnecessary elements
st.markdown("""
  <style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  </style>
""", unsafe_allow_html=True)
