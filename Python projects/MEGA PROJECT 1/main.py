import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary  # Ensure this module exists and includes a `music` dictionary
import requests
import openai
from gtts import gTTS
import pygame
import os

# Install required libraries: pip install pocketsphinx pygame gtts requests openai

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Replace these with your actual API keys
newsapi = "your_newsapi_key_here"  # Replace with your NewsAPI key
openai.api_key = "your_openai_api_key_here"  # Replace with your OpenAI key

def speak(text):
    try:
        tts = gTTS(text)
        tts.save('temp.mp3')
        
        # Initialize Pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Load and play the MP3 file
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        
        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error in speak function: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists("temp.mp3"):
            pygame.mixer.music.unload()
            os.remove("temp.mp3")

def aiProcess(command):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Friday skilled in general tasks like Alexa and Google Cloud. Give short responses, please."},
                {"role": "user", "content": command}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in aiProcess: {e}")
        return "I couldn't process your request. Please try again."

def processCommand(c):
    try:
        if "open google" in c.lower():
            webbrowser.open("https://google.com")
        elif "open facebook" in c.lower():
            webbrowser.open("https://facebook.com")
        elif "open youtube" in c.lower():
            webbrowser.open("https://youtube.com")
        elif "open linkedin" in c.lower():
            webbrowser.open("https://linkedin.com")
        elif c.lower().startswith("play"):
            song = " ".join(c.lower().split()[1:])
            if hasattr(musicLibrary, 'music') and song in musicLibrary.music:
                link = musicLibrary.music[song]
                webbrowser.open(link)
            else:
                speak("Song not found in the library.")
        elif "news" in c.lower():
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                if articles:
                    for article in articles[:5]:  # Limit to the first 5 articles
                        speak(article['title'])
                else:
                    speak("No news articles found.")
            else:
                speak("Failed to fetch news. Please check your API key or connection.")
        elif "exit" in c.lower():
            speak("Goodbye!")
            exit()
        else:
            output = aiProcess(c)
            speak(output)
    except Exception as e:
        print(f"Error in processCommand: {e}")
        speak("Sorry, something went wrong while processing your command.")

if __name__ == "__main__":
    speak("Initializing Friday....")
    while True:
        try:
            print("Listening for wake word...")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)  # Handle background noise
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            word = recognizer.recognize_google(audio)
            if word.lower() == "friday":
                speak("Yes")
                try:
                    with sr.Microphone() as source:
                        print("Friday Active. Listening for command...")
                        recognizer.adjust_for_ambient_noise(source)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)
                except sr.UnknownValueError:
                    speak("Sorry, I didn't understand that.")
                except sr.RequestError:
                    speak("Could not request results. Please check your internet connection.")
        except sr.UnknownValueError:
            print("Wake word not detected.")
        except sr.RequestError:
            print("Speech recognition request error. Please check your internet connection.")
