# # # import moviepy
# # # # from moviepy.video.io.VideoFileClip import VideoFileClip
# # # # print("MoviePy is working!")
# # # from moviepy.editor import VideoFileClip
# # # print("MoviePy is working!")

# # # #   "bastard", "bitch", "motherfucker", "son of a bitch", "cunt", "cock", "dick", "twat", 
# # # #     "faggot", "dyke", "scumbag", "douchebag", "prick", "shithead", "fuck", "bastard", "ass", "whore", 
# # # #     "slut", "pussy", "bitching", "cockfucker", "shit", "crap", "piss", "jerk", "freak", "fuckface", 
# # # #     "fucker", "damn", "hell", "twat", "dickhead", "freak", "shitfaced", "fucked", "motherfucking", "asswipe", 
# # # #     "dickwad", "cockhead", "slutty", "cum", "orgasm", "porn", "cocksucker", 
# # # #     "fisting", "bitchass", "sex", "fuckedup", "broke", "slutbag", "cumshot", "fucking", "ballsack", 
# # # #     "buttfuck", "cocksucker", "clit", "fuckedoff", "clitlicker", "cumdumpster", "minger", "chav", 
# # # #     "dickrider", "dirty whore", "prick", "fuckface", "assfucker", "dicklips", "shag", "bitchslap",
# # # #     "kutti", "kutta", "randi", "randwa", "bharwa", "begherat", "zalil", "behenchod", "madarchod", "saala", 
# # # #     "gandu", "chutiya", "laude", "chalu", "kameena", "jhoota", "gandagi", "bhens ka bacha", "sali", 
# # # #     "bhen ke tukde", "puddi", "bitch", "behaya", "paindo ka baap", "bastard", "saale ka launda", "randi", 
# # # #     "fakra", "kharab", "garbage", "fuck", "meetha launda", "lalu", "ch***", "sala launda", "gandi", "kali", 
# # # #     "bhr*ti", "tatti", "khalay", "l**d", "l*nda", "gandagi", "sadar launda", "panoti", "jhunjhuna", "sahi jaane", 
# # # #     "machi", "patakha", "lagay raho", "sanki", "g***", "laura", "paki", "lalchi", "pagal", "ch**tiya", "f**ki", 
# # # #     "bhadwa", "badmash", "sahi kaam", "g**nd ka tukda", "bhen ke tukde", "pooch", "l**nday", "teri maa", "son of a bitch", 
# # # #     "l***", "chutiyapa", "gandhi g**nd", "bap ka kutta", "ganda", "bhoond", "ghaleez", "angrez ka launda", 
# # # #     "kapayla", "g*****a", "daku", "kali bhen", "saalay", "bacha", "dickhead", "machi ka launda", "nashay ka bacha", 
# # # #     "s**k", "bhainchod", "tapori", "gali dena", 
# # # #     "lal", "padi", "bharwa", "jahanumi", "gandhi g**nd", "kalli randi", "kaali behaya", "punda", "behen ka launda", 
# # # #     "pachayee ka bacha", "chuchi", "nanga", "dundal", "meetha launda", "seelay ka bacha", "khote", "bhondu", 

# # import nltk
# # from nltk.tokenize import word_tokenize
# # from nltk.corpus import stopwords
# # from nltk.stem import WordNetLemmatizer

# # # Step 1: Download NLTK resources
# # nltk.download('punkt')
# # nltk.download('stopwords')
# # nltk.download('wordnet')

# # # Step 2: Define profanity words
# # profanity_words = ["khota", "kameena", "gandi", "badmaash", "randi"]

# # # Step 3: Functions for text processing
# # def preprocess_text(text):
# #     """Tokenize, remove stop words, and lemmatize the input text."""
# #     # Tokenize the text
# #     words = word_tokenize(text)

# #     # Remove stop wor
# #     stop_words = set(stopwords.words('english'))
# #     filtered_words = [word for word in words if word.lower() not in stop_words]

# #     # Lemmatize the words
# #     lemmatizer = WordNetLemmatizer()
# #     lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

# #     return lemmatized_words

# # def check_profanity(text):
# #     """Detect profane words in the text."""
# #     processed_words = preprocess_text(text)
# #     detected_words = [word for word in processed_words if word.lower() in profanity_words]
# #     return detected_words

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# import time

# # Step 1: Set up ChromeDriver
# # Replace 'path/to/chromedriver' with the actual path to your ChromeDriver executable
# chrome_driver_path = "path/to/chromedriver"

# # Step 2: Configure Selenium options
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode (no browser UI)
# options.add_argument("--disable-gpu")  # Disable GPU for headless mode
# options.add_argument("--mute-audio")  # Mute audio to avoid noise

# # Step 3: Initialize the WebDriver
# service = Service(chrome_driver_path)
# driver = webdriver.Chrome(service=service, options=options)

# try:
#     # Step 4: Open the YouTube live stream URL
#     live_url = "https://www.youtube.com/live/TvlyU9GlwN0?si=k2rsNooAyN4Q53t7"  # Replace with your live stream URL
#     driver.get(live_url)

#     # Step 5: Wait for the page to load
#     time.sleep(10)  # Adjust the sleep time as needed

#     # Step 6: Print the page title to confirm it's working
#     print("Page Title:", driver.title)

#     # Step 7: Find the video element (optional)
#     video_element = driver.find_element(By.TAG_NAME, "video")
#     if video_element:
#         print("Video element found!")
#     else:
#         print("Video element not found.")

# except Exception as e:
#     print(f"Error: {e}")

# finally:
#     # Step 8: Close the browser
#     driver.quit()
import os
import time
import threading
from flask import Flask, render_template, request, flash, redirect, url_for, Response
import openai
import yt_dlp as youtube_dl
import subprocess
import json

app = Flask(__name__, template_folder="templates")
app.secret_key = '85fd9d3ce69f76d658c5d3b460cc11408731862976e1881c'

# OpenAI API Key
openai.api_key = "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"

# Global variable to store live subtitles
live_subtitles = []
live_profanity_words = []
live_subtitles_lock = threading.Lock()

# Profanity words list
profanity_words = [
    "kutta", "khota", "gandi randi", "randi", "bharwa", "murdar", "zalil", 
    "badmaash launda", "kameena sala", "kameena", "sala", "khusra", "be haya", 
    "kutti", "manhos", "abuse", "randwa"
]

def check_profanity(text):
    words = text.lower().split()
    detected_words = [word for word in words if word in [pw.lower() for pw in profanity_words]]
    return detected_words

def process_live_stream(live_link):
    global live_subtitles, live_profanity_words
    try:
        # Use yt-dlp to get the direct stream URL
        ydl_opts = {
            'format': 'best',
            'extract_audio': True,
            'audio_format': 'wav',
            'forceurl': True,  # Get the direct stream URL
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(live_link, download=False)
            stream_url = info_dict['url']

        # Use ffmpeg to extract audio in real-time
        ffmpeg_command = [
            'ffmpeg',
            '-i', stream_url,  # Input stream URL
            '-f', 'wav',      # Output format
            '-ar', '16000',   # Sample rate
            '-ac', '1',       # Mono audio
            'pipe:1'          # Output to stdout
        ]

        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Continuously transcribe audio
        while True:
            # Read audio data from ffmpeg
            raw_audio = process.stdout.read(16000)  # Read 1 second of audio
            if not raw_audio:
                break

            # Transcribe the audio using OpenAI Whisper API
            transcript = transcribe_audio_with_whisper(raw_audio)
            if transcript:
                # Detect profanity words
                profanity_words_detected = check_profanity(transcript)

                with live_subtitles_lock:
                    live_subtitles.append(transcript)
                    live_profanity_words = profanity_words_detected
                    if len(live_subtitles) > 10:  # Keep only the last 10 subtitles
                        live_subtitles.pop(0)

            # Wait for a few seconds before processing the next chunk
            time.sleep(1)
    except Exception as e:
        print(f"Error processing live stream: {e}")

def transcribe_audio_with_whisper(audio_data):
    try:
        transcript = openai.Audio.transcribe(
            file=audio_data,
            model="whisper-1",
            response_format="text",
            language="en"  # Force English transcription
        )
        return transcript
    except Exception as e:
        print(f"Error transcribing audio with Whisper: {e}")
        return None

@app.route('/live', methods=['GET', 'POST'])
def live_video():
    if request.method == 'POST':
        live_link = request.form.get('live_link')
        if not live_link:
            flash("Please provide a live video link.", "error")
            return redirect(url_for('home'))

        # Start a new thread to process the live stream
        threading.Thread(target=process_live_stream, args=(live_link,)).start()
        return redirect(url_for('live_subtitles'))

    return render_template('live.html')

@app.route('/live_subtitles')
def live_subtitles():
    return render_template('live_subtitles.html')

@app.route('/get_subtitles')
def get_subtitles():
    def generate():
        global live_subtitles, live_profanity_words
        while True:
            with live_subtitles_lock:
                subtitles = "\n".join(live_subtitles)
                profanity_words = live_profanity_words
                data = {
                    "subtitles": subtitles,
                    "profanityWords": profanity_words
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)  # Update subtitles every 1 second
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)