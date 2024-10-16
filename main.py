import os
from pytube import YouTube
from pydub import AudioSegment
from uuid import uuid4
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/download_mp3', methods=['POST'])
def download_mp3():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        yt = YouTube(youtube_url)
        video_stream = yt.streams.filter(only_audio=True).first()
        video_file = video_stream.download()

        # Convert the downloaded file to MP3
        audio_file = video_file.replace('.webm', '.mp3')
        audio = AudioSegment.from_file(video_file)
        audio.export(audio_file, format='mp3')

        os.remove(video_file)  # Remove the original file

        unique_filename = f"{uuid4()}.mp3"
        os.rename(audio_file, unique_filename)

        return jsonify({"download_link": f"/api/downloads/{unique_filename}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
