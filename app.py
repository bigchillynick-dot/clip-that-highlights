import streamlit as st
import requests
import time

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Smart highlight detection for any game, any POV — vertical, TikTok-ready.")

vod_url = st.text_input("Paste your Twitch VOD URL")

# Twitch API credentials from Streamlit secrets
client_id = st.secrets["rnzsvf09n8i0f2kw1zl0xn3ahagzk7"]
client_secret = st.secrets["2yyo6w7h162fwkpqeaia8lkzg99cnn"]

# Function to get VOD metadata from Twitch
def get_vod_info(vod_url, client_id, client_secret):
    vod_id = vod_url.split('/')[-1].split('?')[0].replace('video/', '')

    auth_response = requests.post('https://id.twitch.tv/oauth2/token', {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }).json()
    access_token = auth_response['access_token']

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    vod_response = requests.get(f'https://api.twitch.tv/helix/videos?id={vod_id}', headers=headers).json()
    return vod_response

if vod_url:
    st.info("Fetching VOD metadata from Twitch…")
    vod_data = get_vod_info(vod_url, client_id, client_secret)

    if "data" in vod_data and len(vod_data["data"]) > 0:
        vod_info = vod_data["data"][0]
        st.success(f"VOD Title: {vod_info['title']}")
        st.markdown(f"🕒 Duration: **{vod_info['duration']}**")
        st.markdown(f"📅 Created at: **{vod_info['created_at']}**")
        st.markdown(f"🔗 [Watch VOD on Twitch]({vod_info['url']})")

        # Simulated highlight detection
        highlights = [
            {"timestamp": "00:12:34", "label": "Clutch Escape"},
            {"timestamp": "00:27:10", "label": "Funny Moment"},
            {"timestamp": "00:45:02", "label": "Chat Explodes"},
        ]
        st.success(f"Found {len(highlights)} simulated highlights!")

        estimated_time = len(highlights) * 3  # 3 seconds per clip
        st.markdown(f"⏳ Estimated time to prepare clips: **{estimated_time} seconds**

