import streamlit as st
import subprocess
import ffmpeg
import os

st.set_page_config(page_title="Clip That Highlights", layout="wide")
st.title("🎬 Clip That Highlights")
st.markdown("Paste any Twitch VOD URL and slice clips instantly using Streamlink + ffmpeg.")

vod_url = st.text_input("Paste your Twitch VOD URL", key="vod_input")

def extract_streamlink_url(vod_url):
    try:
        result = subprocess.run(
            ["streamlink", vod_url, "best", "--stream-url"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        st.error("⚠️ Streamlink failed to extract the stream.")
        error_output = getattr(e, "stderr", None)
        if error_output:
            st.text(error_output)
        else:
            st.text(str(e))
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
        error_output = getattr(e, "stderr", None)
        if error_output:
            st.text(error_output.decode("utf-8"))
        else:
            st.text(str(e))
        return False

if vod_url:
    st.info("Extracting stream URL with Streamlink…", icon="🔍")
    m3u8_url = extract_streamlink_url(vod_url)

    if m3u8_url:
        st.success(f"Stream URL: `{m3u8_url}`", icon="✅")

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
        st.warning("Streamlink could not extract a valid stream. Try a different VOD or check access.", icon="⚠️")
