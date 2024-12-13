import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import queue
import wave

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
webrtc_ctx = webrtc_streamer(key="audio", mode=WebRtcMode.SENDONLY, audio_processor_factory=lambda: processor)

if st.button("Save Audio"):
    if webrtc_ctx.state.playing:
        processor.save_audio("output.wav")
        st.success("Audio saved as output.wav")
    else:
        st.error("Audio stream is not active.")
