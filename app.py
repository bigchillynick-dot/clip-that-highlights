import streamlit as st
import requests
import re

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL and extract metadata using the Twitch API.")

# Replace with your Twitch Developer credentials
CLIENT_ID = "your_client_id"
ACCESS_TOKEN = "your_access_token"

vod_url = st.text_input("Paste your Twitch VOD URL", key="vod_input")

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
        return response.json()["data"][0]
    else:
        st.error(f"⚠️ Twitch API error: {response.status_code}")
        st.text(response.text)
        return None

if vod_url:
    video_id = extract_video_id(vod_url)
    if video_id:
        st.info(f"Extracted Video ID: `{video_id}`", icon="🔍")
        metadata = get_vod_metadata(video_id)
        if metadata:
            st.success("VOD Metadata Retrieved
