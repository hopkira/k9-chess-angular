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
        self.stream_audio_thread.start()

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))
        listening = False
        stream_audio_thread.join()

    def on_listening(self):
        print('Service is listening')
        listening = True

    def on_transcription_complete(self):
        print('Transcription completed')
        listening = False
        self.stream_audio_thread.join()

    def on_hypothesis(self, hypothesis):
        print(hypothesis)

listening = True
mycallback = MyRecognizeCallback()
reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
print "Openning audio recording"
p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
while listening:
    data = bytearray(p.stdout.read(1024))
    speech_to_text.recognize_with_websocket(audio=data, recognize_callback=mycallback)
p.kill()
