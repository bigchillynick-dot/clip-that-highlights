import streamlit as st
import requests
import re

# ─────────────────────────────────────────────────────────────
# 🔐 Load Twitch API Credentials from Streamlit Cloud Secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

# ─────────────────────────────────────────────────────────────
# 🎬 Streamlit UI Setup
st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL to extract metadata and resolve the stream URL.")

vod_url = st.text_input("Paste your Twitch VOD URL")
submit = st.button("Submit")

# ─────────────────────────────────────────────────────────────
# 🧠 Utility Functions

def extract_video_id(vod_url):
    match = re.search(r"twitch\.tv/videos/(\d+)", vod_url)
    return match.group(1) if match else None

def get_vod_metadata(video_id):
    url = f"https://api.twitch.tv/helix/videos?id={video_id}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    st.write("🔍 Metadata API status:", response.status_code)
    st.write("📦 Metadata response:", response.json())
    if response.status_code == 200:
        data = response.json().get("data", [])
        return data[0] if data else None
    return None

def get_m3u8_url(video_id):
    gql_url = "https://gql.twitch.tv/gql"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"OAuth {ACCESS_TOKEN}",  # ✅ FIXED: use OAuth instead of Bearer
        "Content-Type": "application/json"
    }
    payload = [{
        "operationName": "PlaybackAccessToken_Template",
        "variables": {
            "isLive": False,
            "login": "",
            "isVod": True,
            "vodID": video_id,
            "playerType": "embed"
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0828119dedb5e1f9a6a7e3f3b6c8e6e7"
            }
        }
    }]
    response = requests.post(gql_url, headers=headers, json=payload)
    st.write("🔁 GraphQL response status:", response.status_code)
    st.write("📦 GraphQL response:", response.json())
    if response.status_code == 200:
        data = response.json()[0].get("data", {}).get("videoPlaybackAccessToken", {})
        token = data.get("value")
        sig = data.get("signature")
        if token and sig:
            return f"https://vod-secure.twitch.tv/{video_id}/index-dvr.m3u8?sig={sig}&token={token}"
    return None

def parse_duration(d):
    h = re.search(r"(\d+)h", d)
    m = re.search(r"(\d+)m", d)
    s = re.search(r"(\d+)s", d)
    total = 0
    if h: total += int(h.group(1)) * 3600
    if m: total += int(m.group(1)) * 60
    if s: total += int(s.group(1))
    return total

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

        if not video_id:
            st.error("❌ Could not extract video ID. Please check the URL format.")
        else:
            metadata = get_vod_metadata(video_id)
            st.write("📦 Metadata object:", metadata)

            if metadata:
                st.success("VOD Metadata Retrieved ✅")
                title = metadata['title']
                duration_str = metadata['duration']
                published = metadata['published_at']

                st.markdown(f"**Title:** {title}")
                st.markdown(f"**Duration:** {duration_str}")
                st.markdown(f"**Published At:** {published}")

                total_seconds = parse_duration(duration_str)
                clip_length = 30
                estimated_clips = total_seconds // clip_length
                estimated_time = estimated_clips * 10

                st.markdown(f"**Estimated Clips:** {estimated_clips}")
                st.markdown(f"**Estimated Processing Time:** {estimated_time} seconds")

                thumb_url = metadata['thumbnail_url'].replace("%{width}", "640").replace("%{height}", "360")
                st.image(thumb_url, caption="VOD Thumbnail")

                m3u8_url = get_m3u8_url(video_id)
                st.write("🎯 Resolved .m3u8 URL:", m3u8_url if m3u8_url else "❌ Failed to resolve stream URL")
            else:
                st.error("❌ No metadata returned. Check your Twitch credentials or video ID.")
