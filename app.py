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
        probe = ffmpeg.probe(m3u8_url, select_streams='a')
        duration = float(probe['format']['duration'])
        peaks = []
        for i in range(0, int(duration), 5):
            out, err = (
                ffmpeg
                .input(m3u8_url, ss=i, t=5)
                .filter('volumedetect')
                .output('null', format='null')
                .run(capture_stdout=True, capture_stderr=True)
            )
            if "max_volume: " in err.decode():
                vol_line = [line for line in err.decode().split('\n') if "max_volume:" in line]
                if vol_line:
                    vol = float(vol_line[0].split(":")[1].strip().replace(" dB", ""))
                    if vol > -10:  # threshold
                        peaks.append(i)
        return peaks
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
    sorted_scores = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)
    selected = []
    used = set()

    for second, score in sorted_scores:
        if len(selected) >= max_clips:
            break
        if all(abs(second - s) > clip_length for s in used):
            selected.append(second)
            used.add(second)
    return sorted(selected)

def slice_and_format_clips(m3u8_url, timestamps, clip_length=35):
    temp_dir = "clips"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    total = len(timestamps)
    status = st.empty()
    clips = []

    with st.spinner("🎬 Slicing clips... hang tight"):
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

            status.text(f"🎬 Clip {i+1}/{total} — ETA: {((total - i - 1) * 8)}s")

    st.success(f"✅ {len(clips)} clips ready!")

      # Display clips in grid
    cols = st.columns(4)
    for i, clip in enumerate(clips):
        with cols[i % 4]:
            st.video(clip)
            st.download_button("Download", open(clip, "rb"), file_name=os.path.basename(clip))


