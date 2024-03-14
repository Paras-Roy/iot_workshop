import argparse

import cv2
# camera = cv2.VideoCapture(0)

import PIL
import os

import pyttsx3
engine = pyttsx3.init()

from pvcheetah import CheetahActivationLimitError, create
from pvrecorder import PvRecorder
import google.generativeai as genai


genai.configure(api_key='AIzaSyDfrENcWWH4HWiNtD3bI-R9muBbtlvumys')
model = genai.GenerativeModel('gemini-pro-vision')

def main():
    # ret, frame = camera.read()
    # cv2.imwrite('img.png',frame)
    preprompt = 'Format of the response must be plain text. Do not return in markdown format only answer in one paragraph without breaks because i have to convert this text to speech for my IOT smart device. Prompt is: '
    prompt = ""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--access_key',
        help='AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)')
    parser.add_argument(
        '--library_path',
        help='Absolute path to dynamic library. Default: using the library provided by `pvcheetah`')
    parser.add_argument(
        '--model_path',
        help='Absolute path to Cheetah model. Default: using the model provided by `pvcheetah`')
    parser.add_argument(
        '--endpoint_duration_sec',
        type=float,
        default=1.,
        help='Duration in seconds for speechless audio to be considered an endpoint')
    parser.add_argument(
        '--disable_automatic_punctuation',
        action='store_true',
        help='Disable insertion of automatic punctuation')
    parser.add_argument('--audio_device_index', type=int, default=-1, help='Index of input audio device')
    parser.add_argument('--show_audio_devices', action='store_true', help='Only list available devices and exit')
    args = parser.parse_args()

    if args.show_audio_devices:
        for index, name in enumerate(PvRecorder.get_available_devices()):
            print('Device #%d: %s' % (index, name))
        return

    # if not args.access_key:
    #     print('--access_key is required.')
    #     return

    cheetah = create(
        access_key="ANZiDE0WDiyzsnRnXsQxBEvEUFdF51IgfV2aSw6xe3WhVWNPXiQ61w==",
        library_path=args.library_path,
        model_path=args.model_path,
        endpoint_duration_sec=args.endpoint_duration_sec,
        enable_automatic_punctuation=not args.disable_automatic_punctuation)

    try:
        print('Cheetah version : %s' % cheetah.version)

        recorder = PvRecorder(frame_length=cheetah.frame_length, device_index=args.audio_device_index)
        recorder.start()
        print('Listening... (It will stop automatically at the end of speech)')

        try:
            while True:
                partial_transcript, is_endpoint = cheetah.process(recorder.read())
                # print(partial_transcript, end='', flush=True)
                prompt += partial_transcript
                if is_endpoint:
                    # print(cheetah.flush())
                    prompt += cheetah.flush()
                    break
        finally:
            recorder.stop()

    except KeyboardInterrupt:
        pass
    except CheetahActivationLimitError:
        print('AccessKey has reached its processing limit.')
    finally:
        cheetah.delete()
    print(prompt)
    img = PIL.Image.open('img.png')
    # response = model.generate_content(preprompt+prompt)
    response = model.generate_content([preprompt+prompt, img])
    response.resolve()
    print(response.text)
    engine.say(response.text)
    engine.runAndWait()
    engine.stop
    os.remove("img.png")


if __name__ == '__main__':
    main()
