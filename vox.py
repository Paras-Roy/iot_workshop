from vosk import Model, KaldiRecognizer
import pyaudio
import json
import google.generativeai as genai
import PIL



model = Model(r'en-in')
recognizer = KaldiRecognizer(model, 16000)

cap = pyaudio.PyAudio()
stream = cap.open(format=pyaudio.paInt16, channels = 1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

genai.configure(api_key='AIzaSyDfrENcWWH4HWiNtD3bI-R9muBbtlvumys')
model = genai.GenerativeModel('gemini-pro-vision')

preprompt = 'Format of the response must be plain text. Do not return in markdown format only answer in one paragraph without breaks because i have to convert this text to speech for my IOT smart device. Prompt is: '


while True:
    data = stream.read(4096)
    if len(data) == 0:
        break
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        prompt = result["text"]
        print(prompt)
        img = PIL.Image.open('img.png')
        response = model.generate_content([preprompt+prompt, img])
        response.resolve()
        print(response.text)
        break