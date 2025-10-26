import streamlit as st
import requests
import ffmpeg
import os

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Smart highlight detection for any game, any POV — vertical, TikTok-ready.")

vod_url = st.text_input("Paste your Twitch VOD URL")

client_id = st.secrets["TWITCH_CLIENT_ID"]
client_secret = st.secrets["TWITCH_CLIENT_SECRET"]

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

# Test stream URL (replace with real Twitch .m3u8 later)
test_stream_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"

if vod_url:
    st.info("Fetching VOD metadata from Twitch…")
    vod_data = get_vod_info(vod_url, client_id, client_secret)

    if "data" in vod_data and len(vod_data["data"]) > 0:
        vod_info = vod_data["data"][0]
        st.success(f"VOD Title: {vod_info['title']}")
        st.markdown(f"🕒 Duration: **{vod_info['duration']}**")
        st.markdown(f"📅 Created at: **{vod_info['created_at']}**")
        st.markdown(f"🔗 [Watch VOD on Twitch]({vod_info['url']})")

        highlight_time = "00:00:10"
        duration = 15
        output_file = "highlight1.mp4"

        st.info(f"Slicing clip at {highlight_time} for {duration} seconds…")
        if slice_clip(test_stream_url, highlight_time, duration, output_file):
            with open(output_file, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)
            st.download_button("Download Highlight Clip", data=video_bytes, file_name=output_file)
        else:
            st.error("Clip slicing failed. Check stream URL or ffmpeg setup.")
    else:
        st.error("Could not fetch VOD info. Please check the URL or your Twitch API credentials.")
import streamlit as st
import requests
import ffmpeg
import os

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Smart highlight detection for any game, any POV — vertical, TikTok-ready.")

vod_url = st.text_input("Paste your Twitch VOD URL")

client_id = st.secrets["TWITCH_CLIENT_ID"]
client_secret = st.secrets["TWITCH_CLIENT_SECRET"]

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

# Test stream URL (replace with real Twitch .m3u8 later)
test_stream_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"

if vod_url:
    st.info("Fetching VOD metadata from Twitch…")
    vod_data = get_vod_info(vod_url, client_id, client_secret)

    if "data" in vod_data and len(vod_data["data"]) > 0:
        vod_info = vod_data["data"][0]
        st.success(f"VOD Title: {vod_info['title']}")
        st.markdown(f"🕒 Duration: **{vod_info['duration']}**")
        st.markdown(f"📅 Created at: **{vod_info['created_at']}**")
        st.markdown(f"🔗 [Watch VOD on Twitch]({vod_info['url']})")

        highlight_time = "00:00:10"
        duration = 15
        output_file = "highlight1.mp4"

        st.info(f"Slicing clip at {highlight_time} for {duration} seconds…")
        if slice_clip(test_stream_url, highlight_time, duration, output_file):
            with open(output_file, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)
            st.download_button("Download Highlight Clip", data=video_bytes, file_name=output_file)
        else:
            st.error("Clip slicing failed. Check stream URL or ffmpeg setup.")
    else:
        st.error("Could not fetch VOD info. Please check the URL or your Twitch API credentials.")
