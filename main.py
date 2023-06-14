import os
import urllib.request
import shutil

from flask import Flask, render_template, request, send_file
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from pytube import YouTube

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_url = request.form.get('audio-url')
        image_url = request.form.get('image-url')

        audio_filename = download_audio_from_youtube(audio_url)

        audio = AudioFileClip(audio_filename)

        with urllib.request.urlopen(image_url) as response, open('image', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        image = ImageClip('image')
        image = image.set_duration(audio.duration)
        image = image.set_fps(24)

        video = concatenate_videoclips([image])
        video = video.set_audio(audio)
        video.write_videofile('video.mp4', codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")

        os.remove('audio')
        os.remove('image')

        return send_file('video.mp4', as_attachment=True)

    return render_template('index.html')


def download_audio_from_youtube(url):
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    audio_filename = "audio"
    audio.download(filename=audio_filename)
    return audio_filename
