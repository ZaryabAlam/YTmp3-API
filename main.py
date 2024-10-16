from flask import Flask, request, jsonify, send_file
import os
from pytube import YouTube
from pydub import AudioSegment
from uuid import uuid4

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

# Create download folder if it doesn't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['POST'])
def download():
    youtube_url = request.json.get('url')

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        yt = YouTube(youtube_url)
        print(f"Downloading: {yt.title}")
        video_stream = yt.streams.filter(only_audio=True).first()
        video_file = video_stream.download(DOWNLOAD_FOLDER)

        # Convert the downloaded file to MP3
        audio_file = video_file.replace('.webm', '.mp3')
        audio = AudioSegment.from_file(video_file)
        audio.export(audio_file, format='mp3')

        os.remove(video_file)  # Remove the original file

        unique_filename = f"{uuid4()}.mp3"
        os.rename(audio_file, os.path.join(DOWNLOAD_FOLDER, unique_filename))

        download_link = f"https://your-vercel-app-url.vercel.app/downloads/{unique_filename}"

        return jsonify({"download_link": download_link})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
