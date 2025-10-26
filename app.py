import streamlit as st
import subprocess
import re

# ─────────────────────────────────────────────────────────────
# 🎬 Streamlit UI Setup
st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL to extract the stream URL using Streamlink.")

vod_url = st.text_input("Paste your Twitch VOD URL")
submit = st.button("Submit")

# ─────────────────────────────────────────────────────────────
# 🧠 Utility Functions

def extract_video_id(vod_url):
    match = re.search(r"twitch\.tv/videos/(\d+)", vod_url)
    return match.group(1) if match else None

def get_m3u8_from_streamlink(vod_url):
    try:
        cmd = ["streamlink", "--stream-url", vod_url, "best"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            st.error("❌ Streamlink failed. Make sure it's installed and the VOD is valid.")
            st.text(result.stderr)
            return None
    except Exception as e:
        st.error(f"❌ Streamlink error: {e}")
        return None

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
        else:
            st.error("❌ Failed to resolve stream URL using Streamlink.")
