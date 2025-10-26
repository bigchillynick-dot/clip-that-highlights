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

def get_valid_stream_url(vod_id):
    playlist_url = f"https://usher.ttvnw.net/vod/{vod_id}.m3u8"
    response = requests.get(playlist_url)
    lines = response.text.splitlines()
    for i in range(len(lines)):
        if lines[i].startswith("#EXT-X-STREAM-INF") and i + 1 < len(lines):
            stream_url = lines[i + 1]
            if stream_url.endswith(".m3u8"):
                return stream_url
    return None

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
        st.error("⚠️ ffmpeg slicing failed. Check the stream URL or ffmpeg setup.")
        st.text(e.stderr.decode('utf-8') if hasattr(e, 'stderr') else str(e))
        return False

if vod_url:
    vod_id = extract_vod_id(vod_url)
    st.info(f"Extracted VOD ID: {vod_id}", icon="🆔")

    st.info("Fetching VOD metadata from Twitch…", icon="🔍")
    vod_data = get_vod_info(vod_id, client_id, client_secret)

    if "data" in vod_data and len(vod_data["data"]) > 0:
        vod_info = vod_data["data"][0]
        st.success(f"VOD Title: {vod_info['title']}", icon="✅")
        st.markdown(f"🕒 Duration: **{vod_info['duration']}**")
        st.markdown(f"📅 Created at: **{vod_info['created_at']}**")
        st.markdown(f"🔗 [Watch VOD on Twitch]({vod_info['url']})")

        m3u8_url = get_valid_stream_url(vod_id)
        if m3u8_url:
            st.info(f"Using stream: `{m3u8_url}`", icon="📺")

            highlight_time = "00:12:30"
            duration = 20
            output_file = "highlight1.mp4"

            st.info(f"Slicing clip at {highlight_time} for {duration} seconds…", icon="✂️")
            result = slice_clip(m3u8_url, highlight_time, duration, output_file)
            st.write(f"Slice result: {result}")

            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, "rb") as f:
                    video_bytes = f.read()

                st.video(video_bytes, format="video/mp4", start_time=0, key="highlight_video")
                st.download_button("Download Highlight Clip", data=video_bytes, file_name=output_file, key="highlight_download")
            else:
                st.error("⚠️ Clip file is missing or empty. Check ffmpeg setup or stream URL.")
        else:
            st.error("❌ Could not find a valid stream in the playlist.")
    else:
        st.error("Could not fetch VOD info. Please check the URL or your Twitch API credentials.", icon="⚠️")
