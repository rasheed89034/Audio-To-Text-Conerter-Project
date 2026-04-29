import streamlit as st
import requests
import time
import base64

# --- 1. APP CONFIGURATION (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="KineticVoice AI Studio", 
    page_icon="🤖", 
    layout="wide"
)

def set_bg_image(image_file):
    """Encodes the local image to base64 and sets it as a fixed background with darker overlay."""
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            /* ADJUST DARKNESS HERE: increased from 0.65 to 0.8 for better contrast */
            .stApp::before {{
                content: "";
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(7, 22, 12, 1); 
                z-index: -1;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"Background image '{image_file}' not found.")

def local_css():
    """Applies Transparent Sidebar and Neon Green UI styling."""
    st.markdown("""
    <style>
    /* Global Text & Transparency */
    .stApp {
        background-color: transparent; 
        color: #E0E0E0;
    }

    /* TRANSPARENT SIDEBAR - Glassmorphism Effect */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.4) !important; /* Low opacity for transparency */
        backdrop-filter: blur(10px); /* Blurs the background pic behind the sidebar */
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Make sidebar text/icons visible on the darker background */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* Professional Action Button (Neon Green) */
    div.stButton > button {
        background-color: #00E676;
        color: #000000;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #00C853;
        box-shadow: 0px 5px 15px rgba(0, 230, 118, 0.4);
    }

    /* File Uploader area - Transparent Glass */
    section[data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 20px;
    }

    /* Result Box (High Contrast) */
    div[data-testid="stNotification"] {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid #00E676 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply Styles and Background
local_css()
set_bg_image("image_10.png")

# --- 3. ASSEMBLYAI API LOGIC ---

UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_ENDPOINT = "https://api.assemblyai.com/v2/transcript"
# HEADERS = {"authorization": API_KEY_ASSEMBLYAI}
try:
    from api_key import API_KEY_ASSEMBLYAI
except ImportError:
    # This matches the name you put in Phase 3, Step 5
    API_KEY_ASSEMBLYAI = st.secrets["ASSEMBLYAI_KEY"]

HEADERS = {"authorization": API_KEY_ASSEMBLYAI}

def upload_file(uploaded_file):
    response = requests.post(UPLOAD_ENDPOINT, headers=HEADERS, data=uploaded_file)
    return response.json()['upload_url']

def start_transcription(audio_url):
    json_data = {
        "audio_url": audio_url,
        "speech_models": ["universal-3-pro"] 
        "language_detection": True
    }
    response = requests.post(TRANSCRIPT_ENDPOINT, json=json_data, headers=HEADERS)
    return response.json()['id']

def get_result(transcript_id):
    polling_url = f"{TRANSCRIPT_ENDPOINT}/{transcript_id}"
    while True:
        response = requests.get(polling_url, headers=HEADERS)
        data = response.json()
        if data['status'] == 'completed':
            return data['text'], None
        elif data['status'] == 'error':
            return None, data['error']
        time.sleep(3)

# --- 4. SIDEBAR CONTENT ---

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("KineticVoice")
    st.info("Using **AssemblyAI Universal-3-Pro** for high-accuracy transcription.")
    st.divider()
    st.subheader("How to Use:")
    st.write("1. 📁 Upload Audio")
    st.write("2. 🚀 Start Job")
    st.write("3. 💾 Save Result")
    st.divider()
    st.caption("Developed by KineticVoice | ML Engineers")

# --- 5. MAIN PAGE CONTENT ---

# Force content into a centered 70% width container
_, center_col, _ = st.columns([1.5, 7, 1.5])

with center_col:
    st.markdown(
        """
        <h1 style='text-align: center; color: #FFFFFF; margin-bottom: 0px;'>
            🎙️ KineticVoice AI Studio
        </h1>
        <p style='text-align: center; color: #000000; font-size: 1.1rem; font-weight: 700;'>
            Convert your lectures, meetings, or voice notes into text instantly.
        </p>
        """, 
        unsafe_allow_html=True
    )
    st.divider()

    uploaded_file = st.file_uploader("Drop your audio file here", type=["wav", "mp3", "m4a"])

    if uploaded_file:
        # Centering the start button
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            start_btn = st.button("🚀 Start Transcription")

        if start_btn:
            with st.status("🤖 AI is listening...", expanded=True) as status:
                st.write("📤 Sending audio to server...")
                audio_url = upload_file(uploaded_file)
                
                st.write("🧠 Processing with Universal-3-Pro...")
                job_id = start_transcription(audio_url)
                
                text, error = get_result(job_id)
                
                if text:
                    status.update(label="✅ Transcription Finished!", state="complete", expanded=False)
                    st.divider()
                    st.subheader("📝 Transcription Result:")
                    
                    # Styled Result Box
                    st.success(text)
                    
                    st.write("") 
                    st.download_button(
                        label="💾 Download Transcription (.txt)",
                        data=text,
                        file_name="KineticVoice_Transcript.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    status.update(label="❌ Failed", state="error")
                    st.error(f"Error: {error}")
