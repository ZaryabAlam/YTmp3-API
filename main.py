import yt_dlp
import os
import re
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

def sanitize_filename(filename):
    # Replace characters that aren't valid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized.strip()

def download_youtube_audio(youtube_url):
    try:
        print("Downloading audio in original format...")

        # Extract video info to get a sanitized title
        with yt_dlp.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            sanitized_title = sanitize_filename(info_dict['title'])

        # In-memory storage for the downloaded audio file
        audio_data = BytesIO()

        # Set yt_dlp options with in-memory file-like object
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best available audio
            'outtmpl': '-',  # Required for in-memory use; prevents file creation
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,  # Disable console output
            'noplaylist': True,  # Only download single video
            'cookiefile': 'cookies.txt',  # Use cookies to bypass restrictions
        }

        # Download and write to in-memory buffer
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            audio_data.write(ydl.prepare_filename(info_dict).encode())

        # Seek to the start of the in-memory buffer
        audio_data.seek(0)

        # Set filename for the file download response
        filename = f"{sanitized_title}.mp3"
        return audio_data, filename

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

@app.route('/convert', methods=['POST'])
def convert_to_audio():
    try:
        # Get the YouTube URL from the POST request
        data = request.json
        youtube_url = data.get('url')

        if not youtube_url:
            return jsonify({"error": "No URL provided"}), 400

        # Call the download function to download the audio
        audio_data, filename = download_youtube_audio(youtube_url)

        if not audio_data:
            return jsonify({"error": "Audio file could not be created"}), 500

        # Send the audio file as a response
        return send_file(audio_data, as_attachment=True, download_name=filename, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)