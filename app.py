import streamlit as st
import re
import os
import shutil
from streamlink import Streamlink
import ffmpeg

# ─────────────────────────────────────────────────────────────
# 🎬 Streamlit UI Setup
st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL to extract stream URL, slice highlights, and auto-format for TikTok.")

vod_url = st.text_input("Paste your Twitch VOD URL")
submit = st.button("Submit")

# ─────────────────────────────────────────────────────────────
# 🧠 Utility Functions

def extract_video_id(vod_url):
    match = re.search(r"twitch\.tv/videos/(\d+)", vod_url)
    return match.group(1) if match else None

def get_m3u8_from_streamlink(vod_url):
    try:
        session = Streamlink()
        streams = session.streams(vod_url)
        if "best" in streams:
            return streams["best"].url
        else:
            st.error("❌ No 'best' stream found. Try a different VOD.")
            return None
    except Exception as e:
        st.error(f"❌ Streamlink error: {e}")
        return None

def slice_and_format_clips(m3u8_url, clip_length=30, max_clips=5):
    st.info("⏳ Starting clip slicing and formatting...")
    temp_dir = "clips"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    progress = st.progress(0)
    status = st.empty()
    clips = []

    for i in range(max_clips):
        start = i * clip_length
        out_path = f"{temp_dir}/clip_{i+1}.mp4"

        try:
            (
                ffmpeg
                .input(m3u8_url, ss=start, t=clip_length)
                .filter('crop', 'iw/2', 'ih', 'iw/4', 0)  # vertical crop
                .output(out_path, format='mp4', vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            clips.append(out_path)
        except ffmpeg.Error as e:
            st.warning(f"⚠️ Clip {i+1} failed: {e}")

        progress.progress((i + 1) / max_clips)
        status.text(f"Clip {i+1}/{max_clips} — ETA: {((max_clips - i - 1) * 8)}s")

    st.success("✅ All clips sliced and formatted!")
    for clip in clips:
        st.video(clip)
        st.download_button("Download Clip", open(clip, "rb"), file_name=os.path.basename(clip))

# ─────────────────────────────────────────────────────────────
# 🚀 Main Logic

if submit:
    st.write("✅ Submit button clicked")
    if not vod_url:
        st.warning("⚠️ No URL detected. Please paste a Twitch VOD link.")
    else:
        st.write("📨 VOD URL received:", vod_url)
        video_id = extract_video_id(vod_url)
        st.write("🔧 Extracted video ID:", video_id)

        m3u8_url = get_m3u8_from_streamlink(vod_url)
        if m3u8_url:
            st.success("✅ Stream URL Resolved")
            st.code(m3u8_url, language="bash")
            slice_and_format_clips(m3u8_url)
        else:
            st.error("❌ Failed to resolve stream URL using Streamlink.")
