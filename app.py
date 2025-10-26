import streamlit as st
import re
import os
import shutil
from streamlink import Streamlink
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

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

def parse_duration_from_m3u8(m3u8_url):
    try:
        clip = VideoFileClip(m3u8_url)
        return int(clip.duration)
    except Exception as e:
        st.warning(f"⚠️ Could not parse duration: {e}")
        return None

def slice_and_format_clips(m3u8_url, total_duration, clip_length=30):
    st.info("⏳ Starting clip slicing and formatting...")
    temp_dir = "clips"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    clip_count = total_duration // clip_length
    estimated_time = clip_count * 10
    progress = st.progress(0)
    status = st.empty()

    clips = []
    for i in range(clip_count):
        start = i * clip_length
        end = start + clip_length
        raw_path = f"{temp_dir}/raw_{i+1}.mp4"
        final_path = f"{temp_dir}/clip_{i+1}.mp4"

        try:
            ffmpeg_extract_subclip(m3u8_url, start, end, targetname=raw_path)
            clip = VideoFileClip(raw_path)
            vertical = resize(clip, height=1080).crop(x_center=clip.w/2, width=607)  # 9:16 crop
            vertical.write_videofile(final_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            clips.append(final_path)
        except Exception as e:
            st.warning(f"⚠️ Clip {i+1} failed: {e}")

        progress.progress((i + 1) / clip_count)
        status.text(f"Clip {i+1}/{clip_count} — ETA: {estimated_time - (i * 10)}s")

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

            duration = parse_duration_from_m3u8(m3u8_url)
            if duration:
                st.markdown(f"**Total Duration:** {duration} seconds")
                slice_and_format_clips(m3u8_url, duration)
            else:
                st.error("❌ Could not determine video duration.")
        else:
            st.error("❌ Failed to resolve stream URL using Streamlink.")
