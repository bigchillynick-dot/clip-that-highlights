import streamlit as st
import re
import os
import shutil
from streamlink import Streamlink
import ffmpeg
import requests
from collections import defaultdict
from datetime import datetime
import math

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

def get_chat_messages(video_id):
    url = f"https://api.twitch.tv/v5/videos/{video_id}/comments"
    headers = {
        "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",  # Public client ID used for chat replay
        "Accept": "application/vnd.twitchtv.v5+json"
    }
    params = {"content_offset_seconds": 0}
    messages = []

    with st.spinner("📥 Downloading chat replay..."):
        while True:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                break
            data = resp.json()
            for comment in data.get("comments", []):
                offset = int(comment["content_offset_seconds"])
                body = comment["message"]["body"]
                messages.append((offset, body))
            if "_next" in data:
                params["cursor"] = data["_next"]
            else:
                break
    return messages

def score_hype(messages):
    hype_scores = defaultdict(int)
    for offset, msg in messages:
        second = int(offset)
        emotes = len(re.findall(r":[a-zA-Z0-9_]+:", msg))
        caps = sum(1 for w in msg.split() if w.isupper() and len(w) > 2)
        spam = len(re.findall(r"(.)\1{4,}", msg))
        hype_scores[second] += emotes * 3 + caps * 2 + spam * 2 + 1
    return hype_scores

def get_top_hype_moments(hype_scores, clip_length=15, max_clips=100):
    sorted_scores = sorted(hype_scores.items(), key=lambda x: x[1], reverse=True)
    selected = []
    used = set()

    for second, score in sorted_scores:
        if len(selected) >= max_clips:
            break
        if all(abs(second - s) > clip_length for s in used):
            selected.append(second)
            used.add(second)
    return sorted(selected)

def slice_and_format_clips(m3u8_url, timestamps, clip_length=15):
    st.info("⏳ Slicing and formatting clips...")
    temp_dir = "clips"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    total = len(timestamps)
    progress = st.progress(0)
    status = st.empty()
    clips = []

    for i, ts in enumerate(timestamps):
        start = max(0, ts - clip_length // 2)
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

        progress.progress((i + 1) / total)
        status.text(f"Clip {i+1}/{total} — ETA: {((total - i - 1) * 8)}s")

    st.success(f"✅ {len(clips)} clips ready!")
    for clip in clips:
        st.video(clip)
        st.download_button("Download Clip", open(clip, "rb"), file_name=os.path.basename(clip))

# ─────────────────────────────────────────────────────────────
# 🚀 Main Logic

if submit:
    if not vod_url:
        st.warning("⚠️ No URL detected. Please paste a Twitch VOD link.")
    else:
        st.write("📨 VOD URL received:", vod_url)
        video_id = extract_video_id(vod_url)
        if not video_id:
            st.error("❌ Could not extract video ID.")
        else:
            m3u8_url = get_m3u8_from_streamlink(vod_url)
            if not m3u8_url:
                st.error("❌ Failed to resolve stream URL.")
            else:
                messages = get_chat_messages(video_id)
                if not messages:
                    st.error("❌ Could not retrieve chat messages.")
                else:
                    hype_scores = score_hype(messages)
                    top_moments = get_top_hype_moments(hype_scores)
                    if not top_moments:
                        st.warning("⚠️ No hype moments found. Try a different VOD.")
                    else:
                        slice_and_format_clips(m3u8_url, top_moments)
