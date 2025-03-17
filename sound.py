from pydub import AudioSegment
from pydub.generators import Sine

# Generate a 0.2-second (200 ms) beep sound at 440 Hz (A4 note)
beep_sound = Sine(440).to_audio_segment(duration=200)  # 200 ms = 0.2 seconds

# Export the beep sound to a file
beep_sound.export("static/audio/beep.wav", format="wav")