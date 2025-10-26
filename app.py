import streamlit as st
import requests
import ffmpeg
import os

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL and slice clips instantly — hype detection coming next.")

vod_url = st.text_input("Paste your Twitch VOD URL", key="vod_input")

client_id = st.secrets["TWITCH_CLIENT_ID"]
client_secret = st.secrets["TWITCH_CLIENT_SECRET"]

def extract_vod_id(vod_url):
    return vod_url.split('/')[-1].split('?')[0].replace('video/', '')

def get_vod_info(vod_id, client_id, client_secret):
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

def get_m3u8_url(vod_id):
    return f"https://usher.ttvnw.net/vod/{vod_id}.m3u8"

def slice_clip(m3u8_url, start_time, duration, output_path):
    try:
        (
            ffmpeg
            .input(m3u8_url, ss=start_time, t=duration)
            .output(output_path, codec='copy')
            .run(overwrite_output=True)
        )
        return True
    except ffmpeg.Error as e:
        st.error(f"ffmpeg error: {e}")
        return False

if vod_url:
    vod_id = extract_vod_id(vod_url)
    st.info(f"Extracted VOD ID: {vod_id}", icon="🆔")

    st.info("Fetching VOD metadata from Twitch…", icon="🔍")
    vod_data = get_vod_info(vod_id, client_id, client_secret)

    if "data" in vod_data and len(vod_data["data"]) > 0:
        vod_info = vod_data["data"][0]
        st.success(f"VOD Title: {vod_info['title']}", icon="✅")
        st.markdown(f"🕒 Duration

