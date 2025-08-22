"""
A voice-controlled meeting scheduling assistant.

This script listens for a voice command to schedule a meeting, then conversationally
gathers the necessary details (email, date, time), confirms them with the user,
and sends the final information as a single command string to an n8n webhook.
"""

import speech_recognition as sr
import requests
import pyttsx3
import re
import sys
import json
from datetime import datetime

# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================
CONFIG = {
    "N8N_WEBHOOK_URL": "http://localhost:5678/webhook/my-webhook",
    "RECOGNIZER_SETTINGS": {
        "pause_threshold": 1.0,
        "phrase_threshold": 0.3,
        "non_speaking_duration": 0.8
    },
    "PROMPTS": {
        "email": "What is the guest's email address? Please spell it out using words like 'at' and 'dot'.",
        "date": "What is the date for the meeting?",
        "start_time": "And the start time?",
        "end_time": "Finally, what is the end time?"
    },
    "CONFIRMATION_WORDS": ['yes', 'correct', 'right', 'proceed', 'confirm', 'sure'],
    "STOP_COMMANDS": ["stop", "stop the server", "exit", "quit", "goodbye"]
}

# ==============================================================================
# --- INITIALIZATION ---
# ==============================================================================
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# ==============================================================================
# --- CORE UTILITY FUNCTIONS ---
# ==============================================================================
def speak(text):
    """Converts a string of text to audible speech."""
    print(f"🤖 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_input(time_limit=15):
    """
    Listens for a single voice input via the microphone.

    Args:
        time_limit (int): The maximum number of seconds to listen for a phrase.

    Returns:
        str | None: The recognized text, or None if an error occurred.
    """
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Apply recognizer settings from CONFIG
        for key, value in CONFIG["RECOGNIZER_SETTINGS"].items():
            setattr(recognizer, key, value)

        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=time_limit)
            print("🔍 Recognizing...")
            command = recognizer.recognize_google(audio, language='en-IN')
            print(f"👤 You said: {command}")

            if command.lower() in CONFIG["STOP_COMMANDS"]:
                speak("Goodbye!")
                sys.exit()
            
            return command.strip()

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            speak("Sorry, I couldn't quite catch that.")
            return None
        except sr.RequestError:
            speak("The speech recognition service seems to be unavailable.")
            return None

# ==============================================================================
# --- DATA PROCESSING & VALIDATION ---
# ==============================================================================
def process_email_string(text):
    """Cleans up a spoken email address string by replacing spoken words."""
    if not text:
        return ""
    
    replacements = {
        " at the rate ": "@", " at ": "@", " dot ": ".", " underscore ": "_",
        " dash ": "-", " hyphen ": "-",
    }
    processed_text = text.lower()
    for old, new in replacements.items():
        processed_text = processed_text.replace(old, new)
    
    return processed_text.replace(" ", "")

def is_valid_email(email):
    """Checks if a string matches a valid email format using regex."""
    if email:
        regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        return re.search(regex, email)
    return False

# ==============================================================================
# --- MAIN CONVERSATIONAL LOGIC ---
# ==============================================================================
def ask_and_confirm(prompt, time_limit=15, process_func=None, validate_func=None):
    """
    A flexible function to ask a question, process/validate the response,
    and loop until the user confirms it's correct.
    """
    while True:
        speak(prompt)
        response = listen_for_input(time_limit=time_limit)
        if not response:
            continue

        processed_response = process_func(response) if process_func else response

        if validate_func and not validate_func(processed_response):
            speak(f"That doesn't seem to be a valid format. Let's try again.")
            continue

        speak(f"Did you say '{processed_response}'?")
        confirmation = listen_for_input(time_limit=5)

        if confirmation and any(word in confirmation.lower() for word in CONFIG["CONFIRMATION_WORDS"]):
            return processed_response
        else:
            speak("My mistake. Let's try that again.")

def send_to_n8n(command_text):
    """Sends a single command sentence to the n8n webhook."""
    try:
        speak("Perfect. Sending details to the scheduling service...")
        payload = {"command": command_text}
        
        # BUG FIX: Pass the dictionary directly to 'json'. 'requests' handles the conversion.
        response = requests.post(CONFIG["N8N_WEBHOOK_URL"], json=payload)

        if 200 <= response.status_code < 300:
            try:
                return response.json().get('message', "Meeting scheduled successfully.")
            except json.JSONDecodeError:
                return "Meeting scheduled, but no response message was received."
        else:
            return f"Error: Workflow responded with status {response.status_code}. Details: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Could not connect to the scheduling service. Error: {e}"

def schedule_meeting_flow():
    """Guides the user through the meeting scheduling process."""
    speak("Sure, I can help you schedule a meeting.")
    
    meeting_details = {}
    meeting_details['email'] = ask_and_confirm(
        CONFIG["PROMPTS"]["email"],
        time_limit=45,
        process_func=process_email_string,
        validate_func=is_valid_email
    )
    meeting_details['date'] = ask_and_confirm(CONFIG["PROMPTS"]["date"])
    meeting_details['startTime'] = ask_and_confirm(CONFIG["PROMPTS"]["start_time"])
    meeting_details['endTime'] = ask_and_confirm(CONFIG["PROMPTS"]["end_time"])

    # This final confirmation is part of your original logic
    final_prompt = (
        f"Just to confirm:\n"
        f"A meeting with {meeting_details['email']}\n"
        f"on {meeting_details['date']}\n"
        f"from {meeting_details['startTime']} to {meeting_details['endTime']}.\n"
        f"Is that correct?"
    )
    speak(final_prompt)
    
    confirmation = listen_for_input(time_limit=5)
    if confirmation and any(word in confirmation.lower() for word in CONFIG["CONFIRMATION_WORDS"]):
        # Reconstruct the command string as per your original logic
        command_text = (f"schedule a meeting with {meeting_details['email']} on "
                        f"{meeting_details['date']} from {meeting_details['startTime']} "
                        f"to {meeting_details['endTime']}")
        
        response_message = send_to_n8n(command_text)
        speak(response_message)
    else:
        speak("Okay, I’ve cancelled the request.")

# ==============================================================================
# --- SCRIPT EXECUTION ---
# ==============================================================================
if __name__ == "__main__":
    speak("Hello! How can I help you?")
    initial_command = listen_for_input()

    if initial_command and "schedule" in initial_command.lower() and "meeting" in initial_command.lower():
        schedule_meeting_flow()
    elif initial_command:
        speak("Sorry, I didn’t understand. Please say 'schedule a meeting' to begin.")