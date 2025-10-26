import streamlit as st
import re
import os
import shutil
from streamlink import Streamlink
import ffmpeg
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# 🎬 Streamlit UI Setup
st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL to auto-detect hype and generate up to 100 vertical highlight clips.")

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

def get_audio_peaks(m3u8_url):
    try:
        out_path = "volume_log.txt"
        (
            ffmpeg
            .input(m3u8_url)
            .output("null", format="null")
            .global_args("-af", "volumedetect")
            .global_args("-f", "null")
            .global_args("-hide_banner")
            .run(capture_stdout=True, capture_stderr=True)
        )
        # Placeholder: simulate volume spikes
        return [60, 120, 180, 240, 300, 360, 420, 480, 540, 600]
    except Exception as e:
        st.warning(f"⚠️ Audio analysis failed: {e}")
        return []

def score_hype(chat_scores, audio_peaks):
    fusion_scores = defaultdict(int)
    for ts in audio_peaks:
        fusion_scores[ts] += 10
    for ts, score in chat_scores.items():
        fusion_scores[ts] += score
    return fusion_scores

def get_top_hype_moments(fusion_scores, clip_length=35, max_clips=100):
    sorted_scores = sorted
