import sounddevice as sd
import numpy as np
import speech_recognition as sr
import soundfile as sf
import os

# Folder for temporary audio
TEMP_AUDIO_PATH = os.path.join(os.getcwd(), "temp_audio.wav")

# Record audio
def record_audio(duration=5, fs=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.astype(np.float32).flatten(), fs

# Save to WAV and recognize
def recognize_from_audio(audio_data, fs):
    r = sr.Recognizer()
    
    # Save audio to temp WAV file (overwrite each time)
    sf.write(TEMP_AUDIO_PATH, audio_data, fs)
    
    with sr.AudioFile(TEMP_AUDIO_PATH) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            print("You said:", text)
        except sr.UnknownValueError:
            print("Could not understand audio")
            text = None
        except sr.RequestError as e:
            print("Could not request results; check your internet connection")
            text = None
            
    # Optionally remove temp file
    if os.path.exists(TEMP_AUDIO_PATH):
        os.remove(TEMP_AUDIO_PATH)
    return text

# Run
audio_data, fs = record_audio(duration=5)
recognized_text = recognize_from_audio(audio_data, fs)
