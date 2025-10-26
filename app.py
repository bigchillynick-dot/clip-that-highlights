import streamlit as st
import requests
import re

# ─────────────────────────────────────────────────────────────
# 🔧 Twitch API Credentials
CLIENT_ID = "your_client_id"         # Replace with your Twitch Client ID
ACCESS_TOKEN = "your_access_token"   # Replace with your OAuth token

# ─────────────────────────────────────────────────────────────
# 🎬 Streamlit UI Setup
st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL and extract metadata using the Twitch API.")

vod_url = st.text_input("Paste your Twitch VOD URL")
submit = st.button("Submit")

# ─────────────────────────────────────────────────────────────
# 🧠 Utility Functions

def extract_video_id(vod_url):
    """Extracts the video ID from a Twitch VOD URL."""
    match = re.search(r"twitch\.tv/videos/(\d+)", vod_url)
    return match.group(1) if match else None

def get_vod_metadata(video_id):
    """Fetches metadata for a given Twitch video ID using the Twitch API."""
    url = f"https://api.twitch.tv/helix/videos?id={video_id}"
    headers
