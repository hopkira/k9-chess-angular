# You need to install pyaudio to run this example
# pip install pyaudio

from __future__ import print_function
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback

import os, sys, subprocess, threading

STTusername = os.environ['WTTSusername']
STTpassword = os.environ['WTTSpassword']

speech_to_text = SpeechToTextV1(
    username=STTusername,
    password=STTpassword,
    url='https://stream.watsonplatform.net/speech-to-text/api')

print ("Username: " + str(STTusername))
print ("Password: " + str(STTpassword))

# Example using websockets
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        print(transcript)

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        print('Service is listening')

    def on_transcription_complete(self):
        print('Transcription completed')

    def on_hypothesis(self, hypothesis):
        print(hypothesis)

listening = True
mycallback = MyRecognizeCallback()
record = "arecord -d 5 -f S16_LE -r 16000 -t wav my_voice.wav"
p = subprocess.Popen(record, shell=True)
with open(my_voice) as f:
    speech_to_text.recognize_with_websocket(audio=f,content_type='audio/l16; rate=16000', recognize_callback=mycallback)
