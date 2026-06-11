import streamlit as st
import requests
import time

API_BASE = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="VocalSync AI", layout="centered")

st.title("VocalSync AI")
st.write("Upload a video and get it dubbed in your chosen language.")

languages_response = requests.get(f"{API_BASE}/languages")
languages = languages_response.json()["languages"]

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
target_language = st.selectbox("Target Language", options=list(languages.keys()), format_func=lambda x: languages[x])

if st.button("Start Dubbing"):
    if uploaded_file is None:
        st.error("Please upload a video file first.")
    else:
        with st.spinner("Uploading video..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "video/mp4")}
            params = {"target_language": target_language}
            response = requests.post(f"{API_BASE}/jobs", files=files, params=params)

        if response.status_code != 200:
            st.error(f"Upload failed: {response.text}")
        else:
            job_id = response.json()["job_id"]
            st.success(f"Job created. ID: {job_id}")

            progress_bar = st.progress(0)
            status_text = st.empty()

            while True:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}")
                job = status_response.json()

                progress = int(job["progress"])
                status = job["status"]

                progress_bar.progress(progress)
                status_text.write(f"Status: {status} | Progress: {progress}%")

                if status == "done":
                    st.success("Dubbing complete. Downloading video...")
                    download_response = requests.get(f"{API_BASE}/jobs/{job_id}/download")
                    st.download_button(
                        label="Download Dubbed Video",
                        data=download_response.content,
                        file_name=f"vocalsync_{job_id}.mp4",
                        mime="video/mp4"
                    )
                    break

                elif status == "failed":
                    st.error(f"Job failed: {job.get('error_message', 'Unknown error')}")
                    break

                time.sleep(3)