import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from docx import Document
from io import BytesIO

# Load all the environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title='Youtube Notesgen',
    page_icon=':clapper:',
    layout='wide',
    initial_sidebar_state='collapsed',
)

# Configure the Google API
genai.configure(api_key=os.getenv("Give yoyr GOOGLE_API_KEY here"))

# Prompt for video Notes Gen
prompt = """You are YouTube NotesGen, an AI-powered note-taking assistant. You have watched the video based on the provided transcript and understand its content. Your goal is to create concise, comprehensive, 
and easy-to-understand notes summarizing the key points of the video. Imagine you are summarizing the video for someone who hasn't watched it. Your objective is to deliver top-notch notes, rated 10/10 for clarity,
 coherence, and informativeness. Utilize the provided transcript to craft the best possible notes, ensuring they are insightful, well-structured, and easily digestible. """

# Function to get the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        # Extract the video ID from a YouTube URL using regex
        video_id_match = re.search(r"(?<=v=)[^&#]+", youtube_video_url) or re.search(r"(?<=youtu\.be/)[^&#]+", youtube_video_url)
        video_id = (video_id_match.group(0) if video_id_match else None)

        # Handle cases where the video ID could not be extracted
        if not video_id:
            st.error("Could not extract video ID from the URL.")
            return None
            
        # Get the transcript
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(i["text"] for i in transcript_text)
        return transcript

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video: {}. Please try a different video.".format(youtube_video_url))
        return None
    except Exception as e:
        st.error("An error occurred while retrieving the transcript. Please check the video URL and try again.")
        return None

# Function to get the summary or notes based on the prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error("An error occurred while generating the summary and notes.")
        return None

# Function to create the Word document
def generate_word_document(content):
    doc = Document()
    doc.add_paragraph(content)
    byte_io = BytesIO()
    doc.save(byte_io)
    byte_io.seek(0)
    return byte_io

# Streamlit Interface
def streamlit_ui():
    # Set background image or color
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://res.cloudinary.com/dwmwpmrpo/image/upload/v1711466747/wwlylo11yjeiwxid4393.jpg");
            background-size: cover;
        }
        div.stAlert {
            background-color: #ffffff; 
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([0.3, 1.8])
    col1.image('http://res.cloudinary.com/dwmwpmrpo/image/upload/v1711467616/l2dzplxuuozzgf3fkuge.png', width=300)
    # Input form
    with st.container():
        youtube_link = st.text_input(label="YouTube Video URL", placeholder="https://www.youtube.com/watch?v=abcdefghijk")
        
        generate_button = st.button(label="Generate Notes")

        if generate_button and youtube_link:
            with st.spinner('🔄 Generating Notes...'):
                transcript_text = extract_transcript_details(youtube_link)
                if transcript_text:
                    summary = generate_gemini_content(transcript_text, prompt)
                    if summary:
                        st.subheader("Notes")
                        st.info(summary)
                        word_file = generate_word_document(summary)
                        word_bytes = word_file.getvalue()  # Ensure you are using getvalue() here
                        st.download_button(
                            label="Download Notes as Word",
                            data=word_bytes,
                            file_name="YouTube_Notes.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Couldn't fetch the transcript. Make sure the video has accessible transcripts.")


    # Custom styles
    st.write('<style>.stButton>button{border: 2px solid #000000; border-radius: 20px; color: black;}</style>', unsafe_allow_html=True)

# Hide Streamlit default footer and hamburger menu
def hide_footer_style():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .css-1d391kg {display:none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    hide_footer_style()
    streamlit_ui()
