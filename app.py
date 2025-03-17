import os
import time
import uuid
import sqlite3
from flask import Flask, render_template, request, flash, session, redirect, url_for, send_file
from moviepy.editor import VideoFileClip
import openai
import yt_dlp as youtube_dl
from pydub import AudioSegment
from pydub.utils import make_chunks
from textblob import TextBlob  # For sentiment analysis

app = Flask(__name__, template_folder="templates")
app.secret_key = '85fd9d3ce69f76d658c5d3b460cc11408731862976e1881c'

# OpenAI API Key
openai.api_key = "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"

# Ensure directories exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Profanity words list
profanity_words = [
    "kutta", "khota", "gandi randi", "randi", "bharwa", "murdar", "zalil", 
    "badmaash launda", "kameena sala", "kameena", "cat", "khusra", "be haya", 
    "kutti", "manhos", "abuse", "randwa", "the", "dog", "crazy"
]

def check_profanity(text):
    words = text.lower().split()
    detected_words = [word for word in words if word in [pw.lower() for pw in profanity_words]]
    return detected_words

def get_content_rating(detected_words, sentiment_polarity, video_length):
    """
    Determine content rating based on profanity, sentiment, and video length.
    """
    if video_length <= 2:  # Short video
        mild_threshold = 2
        explicit_threshold = 4
    elif video_length <= 10:  # Medium video
        mild_threshold = 3
        explicit_threshold = 6
    else:  # Long video
        mild_threshold = 5
        explicit_threshold = 8

    if not detected_words and sentiment_polarity >= 0:
        return "Clean (G) 🟢 Safe", "No bad words, no violence."
    elif len(detected_words) <= mild_threshold or (sentiment_polarity < 0 and sentiment_polarity >= -0.5):
        return "Mild (PG) 🟡 Moderate", "Some strong words, mild action."
    else:
        return "Explicit (R/18+) 🔴 Restricted", "Strong language, violence, or adult content."

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.
    Returns a tuple (polarity, subjectivity).
    Polarity ranges from -1 (negative) to 1 (positive).
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity

def init_db():
    connection = sqlite3.connect('mydatabase.db')
    cursor = connection.cursor()
    
    # Check if the content_rating column exists
    cursor.execute("PRAGMA table_info(videos)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'content_rating' not in column_names:
        # Add the content_rating column if it doesn't exist
        cursor.execute("ALTER TABLE videos ADD COLUMN content_rating TEXT")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT NOT NULL,
            extracted_text TEXT NOT NULL,
            profanity_words TEXT,
            profanity_status BOOLEAN,
            content_rating TEXT,  -- New column for content rating
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    connection.commit()
    connection.close()
    print("Database initialized successfully!")

def save_to_database(video_name, extracted_text, profanity_words, profanity_status, content_rating):
    connection = sqlite3.connect('mydatabase.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO videos (video_name, extracted_text, profanity_words, profanity_status, content_rating)
        VALUES (?, ?, ?, ?, ?)
    """, (video_name, extracted_text, ', '.join(profanity_words), profanity_status, content_rating))
    connection.commit()
    connection.close()

def split_audio(audio_path, chunk_length_ms=300000):
    audio = AudioSegment.from_file(audio_path)
    chunks = make_chunks(audio, chunk_length_ms)
    return chunks

def compress_audio(audio_path, output_path, bitrate="64k"):
    audio = AudioSegment.from_file(audio_path)
    audio.export(output_path, format="wav", bitrate=bitrate)
    audio = None  # Release the AudioSegment object

def transcribe_audio_with_whisper(audio_path, language="auto"):
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="text",
                language=language if language != "auto" else None  # Use 'auto' if language is not specified
            )
        return transcript
    except Exception as e:
        print(f"Error transcribing audio with Whisper: {e}")
        return None

def clear_temporary_files():
    for file in os.listdir('static/audio'):
        file_path = os.path.join('static/audio', file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                print(f"File {file_path} is still in use. Retrying in 1 second...")
                time.sleep(1)  # Wait for 1 second
                os.remove(file_path)  # Try again

    for file in os.listdir('static/uploads'):
        file_path = os.path.join('static/uploads', file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                print(f"File {file_path} is still in use. Retrying in 1 second...")
                time.sleep(1)  # Wait for 1 second
                os.remove(file_path)  # Try again

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    # Clear session data and temporary files before processing a new video
    session.clear()
    session['session_id'] = str(uuid.uuid4())  # Add a unique session ID
    clear_temporary_files()

    # Get file, link, and language from the form
    file = request.files.get('file')
    link = request.form.get('link')
    language = request.form.get('language', 'auto')  # Default to 'auto' if not provided

    if not file and not link:
        flash("Please upload a video file or provide a video link.", "error")
        return redirect(url_for('home'))

    # Handle file upload
    if file:
        allowed_extensions = {'mp4', 'mkv', 'avi', 'mov'}
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            flash("Invalid file type. Please upload a video file with extensions: .mp4, .mkv, .avi, or .mov.", "error")
            return redirect(url_for('home'))

        video_path = os.path.join('static/uploads', file.filename)
        try:
            file.save(video_path)
            print(f"File saved successfully at: {video_path}")  # Debug statement
            session['video_path'] = video_path
            session['language'] = language  # Save selected language in session
        except Exception as e:
            print(f"Error saving file: {e}")  # Debug statement
            flash(f"Error saving the video file: {str(e)}", "error")
            return redirect(url_for('home'))

    # Handle video link
    elif link:
        # Validate the link
        if not (link.startswith('http://') or link.startswith('https://')):
            flash("Invalid video link. Please provide a valid URL.", "error")
            return redirect(url_for('home'))
        
        # Download video from link using yt-dlp
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join('static', 'uploads', f'%(title)s_{int(time.time())}.%(ext)s'),
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            # After downloading, get the filename of the downloaded video
            downloaded_video = os.listdir(os.path.join('static', 'uploads'))[-1]
            video_path = os.path.join('static', 'uploads', downloaded_video)
            session['video_path'] = video_path
            session['language'] = language  # Save selected language in session
            print(f"Downloaded video path: {video_path}")  # Debug statement
        except Exception as e:
            flash(f"Error downloading the video: {str(e)}", "error")
            return redirect(url_for('home'))

    return redirect(url_for('process_video'))

@app.route('/process', methods=['GET'])
def process_video():
    video_path = session.get('video_path')
    language = session.get('language', 'auto')  # Get selected language from session
    print(f"Processing video: {video_path}")  # Debug statement

    if not video_path:
        flash("No video to process.", "error")
        return redirect(url_for('home'))

    try:
        # Verify that the video file exists
        if not os.path.exists(video_path):
            flash("Video file not found.", "error")
            return redirect(url_for('home'))

        # Extract audio from video
        video = VideoFileClip(video_path)
        audio_path = os.path.join('static/audio', 'extracted_audio.wav')
        video.audio.write_audiofile(audio_path, fps=16000)

        # Calculate video length in minutes
        video_length = video.duration / 60  # Convert duration from seconds to minutes
        video.close()  # Close the VideoFileClip object
        session['audio_path'] = audio_path
        print(f"Extracted audio from: {video_path}")  # Debug statement

        # Split audio into smaller chunks (5 minutes each)
        chunks = split_audio(audio_path)
        full_transcript = ""
        sentiment_results = []  # Store sentiment analysis results

        # Transcribe each chunk
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join('static/audio', f'chunk_{i}.wav')
            chunk.export(chunk_path, format="wav")

            # Compress the chunk to reduce file size
            compressed_chunk_path = os.path.join('static/audio', f'compressed_chunk_{i}.wav')
            compress_audio(chunk_path, compressed_chunk_path, bitrate="64k")

            # Transcribe the compressed chunk
            transcript = transcribe_audio_with_whisper(compressed_chunk_path, language)
            if transcript:
                full_transcript += transcript + " "
                print(f"Transcribed chunk {i}: {transcript[:50]}...")  # Debug statement

                # Analyze sentiment
                sentiment_polarity = analyze_sentiment(transcript)
                sentiment_results.append((transcript, sentiment_polarity))
            else:
                flash(f"Failed to transcribe chunk {i}.", "error")

        if not full_transcript:
            flash("Failed to transcribe audio.", "error")
            return redirect(url_for('home'))

        # Check for profanity
        profanity_words_detected = check_profanity(full_transcript)
        profanity_status = bool(profanity_words_detected)

        # Determine content rating
        sentiment_polarity = analyze_sentiment(full_transcript)
        content_rating, rating_description = get_content_rating(profanity_words_detected, sentiment_polarity, video_length)  # Pass video_length here

        # Save data to session and database
        session['extracted_text'] = full_transcript
        session['profanity_status'] = profanity_status
        session['profanity_words'] = profanity_words_detected
        session['content_rating'] = content_rating
        session['rating_description'] = rating_description
        session['sentiment_results'] = sentiment_results  # Save sentiment results

        save_to_database(
            video_name=os.path.basename(video_path),
            extracted_text=full_transcript,
            profanity_words=profanity_words_detected,
            profanity_status=profanity_status,
            content_rating=content_rating
        )

    except Exception as e:
        flash(f"Error processing the video: {str(e)}", "error")
        return redirect(url_for('home'))

    return redirect(url_for('result'))

@app.route('/result')
def result():
    # Load results from session
    text = session.get('extracted_text', 'No text found')
    profanity_status = session.get('profanity_status', False)
    detected_words = session.get('profanity_words', [])
    content_rating = session.get('content_rating', 'Clean (G) 🟢 Safe')
    rating_description = session.get('rating_description', 'No bad words, no violence.')
    audio_path = session.get('audio_path', None)
    video_path = session.get('video_path', None)
    sentiment_results = session.get('sentiment_results', [])  # Get sentiment results

    return render_template('result.html', text=text, profanity_status=profanity_status, detected_words=detected_words, content_rating=content_rating, rating_description=rating_description, audio_path=audio_path, video_path=video_path, sentiment_results=sentiment_results)

@app.route('/download_audio')
def download_audio():
    audio_path = session.get('audio_path')
    if not audio_path or not os.path.isfile(audio_path):
        flash("Audio file not found or was not processed correctly.", "error")
        return redirect(url_for('home'))
    try:
        return send_file(audio_path, as_attachment=True, download_name='extracted_audio.wav')
    except Exception as e:
        flash(f"Error downloading the audio file: {str(e)}", "error")
        return redirect(url_for('home'))

@app.route('/download_video')
def download_video():
    video_path = session.get('video_path')
    if not video_path or not os.path.isfile(video_path):
        flash("Video file not found or was not downloaded correctly.", "error")
        return redirect(url_for('home'))
    try:
        return send_file(video_path, as_attachment=True, download_name='downloaded_video.mp4')
    except Exception as e:
        flash(f"Error downloading the video: {str(e)}", "error")
        return redirect(url_for('home'))

@app.route('/history')
def history():
    connection = sqlite3.connect('mydatabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    connection.close()
    return render_template('history.html', rows=rows)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)