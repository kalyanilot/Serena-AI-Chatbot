import os
import sounddevice as sd
import numpy as np
import soundfile as sf
import speech_recognition as sr

from ai_engine.emotion_detector import detect_emotion
from ai_engine.response_engine import generate_response
from ai_engine.safety import detect_crisis, crisis_response
from ai_engine.memory_manager import load_memory, save_memory
from ai_engine.tts_utils import speak

# ---------------- AUDIO FUNCTIONS ---------------- #

def record_audio(duration=4, fs=16000):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten(), fs


def recognize_from_audio(audio_data, fs):
    r = sr.Recognizer()
    temp_file = "temp_audio.wav"

    sf.write(temp_file, audio_data, fs)

    try:
        with sr.AudioFile(temp_file) as source:
            audio = r.record(source)
            try:
                return r.recognize_google(audio)
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return ""
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


# ---------------- MAIN PROGRAM ---------------- #

conversation_history = load_memory()

print("\n🧠 Mental Health AI Assistant")
print("1️⃣ Text Mode")
print("2️⃣ Continuous Voice Mode\n")

mode = input("Enter 1 or 2: ").strip()

# -------- TEXT MODE -------- #
if mode == "1":
    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            speak("Take care. You matter. Goodbye.")
            save_memory(conversation_history)
            break

        conversation_history.append({"user": user_input})

        if detect_crisis(user_input):
            reply = crisis_response()
            print(f"\nChatbot: {reply}")
            speak(reply)
            continue

        emotion_data = detect_emotion(user_input)
        emotion = emotion_data["emotion"]

        reply = generate_response(emotion)

        conversation_history.append({"bot": reply})
        save_memory(conversation_history)

        print(f"\nChatbot ({emotion}): {reply}")
        speak(reply)


# -------- VOICE MODE -------- #
elif mode == "2":
    print("\n🗣️ Continuous Voice Mode activated. Say 'exit' to quit.\n")

    while True:
        print("🎤 Listening...")
        audio_data, fs = record_audio()

        user_input = recognize_from_audio(audio_data, fs)

        if not user_input:
            continue

        print(f"You said: {user_input}")

        if user_input.lower() == "exit":
            speak("Goodbye. Take care of yourself.")
            save_memory(conversation_history)
            break

        conversation_history.append({"user": user_input})

        if detect_crisis(user_input):
            reply = crisis_response()
            print(f"Chatbot: {reply}")
            speak(reply)
            continue

        emotion_data = detect_emotion(user_input)
        emotion = emotion_data["emotion"]

        reply = generate_response(emotion)

        conversation_history.append({"bot": reply})
        save_memory(conversation_history)

        # ✅ THIS IS THE PART YOU ASKED FOR (EXACT)
        print(f"Chatbot ({emotion}): {reply}")
        speak(reply)

else:
    print("❌ Invalid choice") 