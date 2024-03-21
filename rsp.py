import json
from time import sleep
import os
import PIL

#camera
from picamera import PiCamera
camera=PiCamera()

#speech to text
from vosk import Model, KaldiRecognizer
import pyaudio
vc_model = Model(r'en-in')
recognizer = KaldiRecognizer(vc_model, 16000)
cap = pyaudio.PyAudio()
stream = cap.open(format=pyaudio.paInt16, channels = 1, rate=16000, input=True, frames_per_buffer=8192)

#button setup
import RPi.GPIO as io
io.setwarnings(False)
io.setmode(io.BCM)

#visual prompt button
io.setup(14,io.IN,pull_up_down=io.PUD_DOWN)
#audio only prompt button
# io.setup(14,io.IN,pull_up_down=io.PUD_DOWN)

#generative model setup
import google.generativeai as genai
genai.configure(api_key='AIzaSyDfrENcWWH4HWiNtD3bI-R9muBbtlvumys')
vis_model = genai.GenerativeModel('gemini-pro-vision')
aud_model = genai.GenerativeModel('gemini-pro')
preprompt = 'Format of the response must be plain text. Do not return in markdown format only answer in one paragraph without breaks because i have to convert this text to speech for my IOT smart device. Prompt is: '

#text to speech setup
from playsound import playsound
import requests

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "63f13c906137c42e83676f8ed6aff484",
}

#function for text to speech
def tts(text):
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    response = requests.post(url, json=data, headers=headers)
    with open("output.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    smth = "output.mp3"  # Replace with your audio file path
    playsound(smth)  # Plays the audio file
    os.remove("output.mp3")


#function for visual based prompting
def vis_button_callback(channel):
        print("-----------------------------------------------------------------------------")
        while True:
            stream.start_stream()
            data = stream.read(4096)
            #if len(data) == 0:
             #   break
            if recognizer.AcceptWaveform(data):
                print("listening...")
                result = json.loads(recognizer.Result())
                prompt = result["text"]
                if(prompt==""):
                        continue
                print(prompt)
                camera.start_preview()
                sleep(2)
                camera.capture('img.jpg')
                camera.stop_preview()
                img = PIL.Image.open('img.jpg')
                response = vis_model.generate_content([preprompt+prompt, img])
                response.resolve()
                print(response.text)
                tts(response.text)
                os.remove('img.jpg')
                stream.stop_stream()
                break

#function for audio only prompting
def aud_button_callback(channel):
        print("-----------------------------------------------------------------------------")
        while True:
            stream.start_stream()
            data = stream.read(4096)
            #if len(data) == 0:
             #   break
            if recognizer.AcceptWaveform(data):
                print("listening...")
                result = json.loads(recognizer.Result())
                prompt = result["text"]
                if(prompt==""):
                        continue
                print(prompt)
                response = aud_model.generate_content([preprompt+prompt])
                response.resolve()
                print(response.text)
                tts(response.text)
                stream.stop_stream()
                break


#adding event handler for visual based prompting
io.add_event_detect(14,io.RISING,callback=vis_button_callback)
#adding event handler for audio only prompting
# io.add_event_detect(14,io.RISING,callback=aud_button_callback)

message=input("Enter any key to exist! \n\n")
io.cleanup()