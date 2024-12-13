import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import queue
import wave
import os
import logging
import logging.handlers
from twilio.rest import Client

logger = logging.getLogger(__name__)

@st.cache_data  # type: ignore
def get_ice_servers():
    """Use Twilio's TURN server because Streamlit Community Cloud has changed
    its infrastructure and WebRTC connection cannot be established without TURN server now.  # noqa: E501
    We considered Open Relay Project (https://www.metered.ca/tools/openrelay/) too,
    but it is not stable and hardly works as some people reported like https://github.com/aiortc/aiortc/issues/832#issuecomment-1482420656  # noqa: E501
    See https://github.com/whitphx/streamlit-webrtc/issues/1213
    """

    # Ref: https://www.twilio.com/docs/stun-turn/api
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    except KeyError:
        logger.warning(
            "Twilio credentials are not set. Fallback to a free STUN server from Google."  # noqa: E501
        )
        return [{"urls": ["stun:stun.l.google.com:19302"]}]

    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    return token.ice_servers

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = queue.Queue()

    def recv(self, frame):
        audio_data = frame.to_ndarray()
        self.audio_buffer.put(audio_data)
        return frame

    def save_audio(self, file_path):
        frames = []
        while not self.audio_buffer.empty():
            frames.append(self.audio_buffer.get())

        audio_data = np.concatenate(frames, axis=0)
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data.tobytes())

st.title("Audio Input App")

st.write("This app captures audio input using `streamlit-webrtc`.")

processor = AudioProcessor()
webrtc_ctx = webrtc_streamer(key="audio", mode=WebRtcMode.SENDONLY,rtc_configuration={"iceServers": get_ice_servers()},
        media_stream_constraints={"video": False, "audio": True},)

st.write(f"WebRTC State: {webrtc_ctx.state}")
st.write(f"Playing: {webrtc_ctx.state.playing}, Signalling: {webrtc_ctx.state.signalling}")


if st.button("Save Audio"):
    if webrtc_ctx.state.playing:
        processor.save_audio("output.wav")
        st.success("Audio saved as output.wav")
    else:
        st.error("Audio stream is not active.")
