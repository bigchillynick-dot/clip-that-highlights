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

vod_url = st.text_input("Paste your Twitch VOD URL", key="vod_input")
submit = st.button("Submit")

# ─────────────────────────────────────────────────────────────
# 🧠 Utility Functions

def extract_video_id(vod_url):
    match = re.search(r"twitch\.tv/videos/(\d+)", vod_url)
    return match.group(1) if match else None

def get_vod_metadata(video_id):
    url = f"https://api.twitch.tv/helix/videos?id={video_id}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return data[0] if data else None
    else:
        st.error(f"⚠️ Twitch API error: {response.status_code}")
        st.text(response.text)
        return None

# ─────────────────────────────────────────────────────────────
# 🚀 Main Logic

if submit and vod_url:
    video_id = extract_video_id(vod_url)
    if video_id:
        st.info(f"Extracted Video ID: `{video_id}`", icon="🔍")
        metadata = get_vod_metadata(video_id)

        if metadata:
            st.success("VOD Metadata Retrieved ✅")
            st.markdown(f"**Title:** {metadata['title']}")
            st.markdown(f"**
