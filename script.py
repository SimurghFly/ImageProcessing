import asyncio
import cv2
import aiohttp
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
import numpy as np

class GoProVideoTrack(VideoStreamTrack):
    def __init__(self, gopro_stream_url):
        super().__init__()
        self.gopro_stream_url = gopro_stream_url
        self.cap = cv2.VideoCapture(self.gopro_stream_url)

    async def recv(self):
        frame = await asyncio.to_thread(self._get_frame)
        if frame is None:
            raise Exception("No frame received from GoPro")
        return frame

    def _get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        # Convert to YUV format as required by WebRTC
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
        return frame

def create_peer_connection():
    pc = RTCPeerConnection()
    return pc

async def main(gopro_url):
    signaling = TcpSocketSignaling("127.0.0.1", 9999)
    pc = create_peer_connection()
    video_track = GoProVideoTrack(gopro_url)
    pc.addTrack(video_track)

    await signaling.connect()

    # Wait for offer from client
    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)

    # Create and send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)

    print("WebRTC stream started.")

    # Keep the connection alive
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Replace with your GoPro RTMP stream URL
    gopro_stream_url = "rtmp://<gopro_stream_url>"
    asyncio.run(main(gopro_stream_url))
