import yt_dlp
import os
import re
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Path where audio files will be stored
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def sanitize_filename(filename):
    # Replace characters that aren't valid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized.strip()

def download_youtube_audio(youtube_url, output_path='.'):
    try:
        print("Downloading audio in original format...")

        # Extract video info to get a sanitized title
        with yt_dlp.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            # Sanitize the title to remove special characters
            sanitized_title = sanitize_filename(info_dict['title'])

        # Update `outtmpl` with sanitized title for direct download
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best available audio
            'outtmpl': os.path.join(output_path, f'{sanitized_title}.%(ext)s'),  # Save with sanitized title
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            downloaded_file_path = os.path.join(output_path, f"{sanitized_title}.{info_dict['ext']}")
            print(f"Audio file saved at: {downloaded_file_path}")
            os.rename(downloaded_file_path, downloaded_file_path)
            return downloaded_file_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/convert', methods=['POST'])
def convert_to_audio():
    try:
        # Get the YouTube URL from the POST request
        data = request.json
        youtube_url = data.get('url')

        if not youtube_url:
            return jsonify({"error": "No URL provided"}), 400

        # Call the download function to download the audio
        audio_file_path = download_youtube_audio(youtube_url, output_path=DOWNLOAD_FOLDER)

        if not audio_file_path or not os.path.exists(audio_file_path):
            return jsonify({"error": "Audio file could not be created"}), 500

        # Send the audio file as a response
        return send_file(audio_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


