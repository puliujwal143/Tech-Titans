import os
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import sounddevice as sd
import wave
import numpy as np

# Load Gemini API key from environment variable
api_key = "AIzaSyBdu9OYqrt_ukO90sEkTChSZiQBeJ3SoyM"
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("Gemini API key is missing. Set it as an environment variable.")

def generate_email(recipient_name, event_details, special_instructions):
    prompt = f"""
    Generate a personalized email:

    Dear {recipient_name},

    {event_details}

    {special_instructions}

    Best regards,
    [Your Name]
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Extract and return generated text
        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            return "Error: No response from Gemini AI."

    except Exception as e:
        return f"Error: {str(e)}"

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results. Check internet connection."

def record_audio(duration=5, samplerate=44100):
    st.info("Recording... Speak now!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype=np.int16)
    sd.wait()
    
    temp_audio_path = "temp_audio.wav"
    with wave.open(temp_audio_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    return temp_audio_path

# Streamlit UI
st.title("AI Personalized Email Generator (Echo Mail)")

recipient_name = st.text_input("Recipient Name")
event_details = st.text_area("Event Details")
special_instructions = st.text_area("Special Instructions")

# Voice recording option
if st.button("Record Voice for Event Details"):
    temp_audio_path = record_audio()
    transcribed_text = transcribe_audio(temp_audio_path)
    st.text_area("Transcribed Text", transcribed_text)
    event_details = transcribed_text  # Use transcribed text as event details

if st.button("Generate Email"):
    if not api_key:
        st.error("Gemini API key is missing. Set it as an environment variable.")
    elif recipient_name and event_details:
        email_content = generate_email(recipient_name, event_details, special_instructions)
        st.subheader("Generated Email:")
        st.write(email_content)
    else:
        st.error("Please provide at least a recipient name and event details.")