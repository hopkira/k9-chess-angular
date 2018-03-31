# You need to install pyaudio to run this example
# pip install pyaudio

from __future__ import print_function
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback
from watson_developer_cloud import ConversationV1

import os, sys, subprocess, threading, time, json, re, signal, snowboydecoder

STTusername = os.environ['WTTSusername']
STTpassword = os.environ['WTTSpassword']

speech_to_text = SpeechToTextV1(
    username=STTusername,
    password=STTpassword,
    url='https://stream.watsonplatform.net/speech-to-text/api')

WAusername = os.environ['WCusername']
WApassword = os.environ['WCpassword']

conversation = ConversationV1(
    username=WAusername,
    password=WApassword,
version='2018-02-16')

WAworkspace_id = os.environ['WCworkspace']

print ("STT Username: " + str(STTusername))
print ("STT Password: " + str(STTpassword))
print ("WA Username: " + str(WAusername))
print ("WA Password: " + str(WApassword))
print ("WA Workspace: " + str(WAworkspace_id))

# Initialise snowboy global variables and methods
model = "./K9.pmdl"
interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

# K9 hotword has been detected
def K9_detected():
    print ("K9 hotword detected...\n")
    global stop_now
    stop_now = True # get the detector to terminate

def stop_snowboy():
    global stop_now
    if (stop_now is True) :
        print ("Snowboy stop interrupt.")
    return stop_now

# Example using websockets
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        pass

    def on_connected(self):
        pass

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        pass

    def on_transcription_complete(self):
        global finished
        finished = True

    def on_hypothesis(self, hypothesis):
        global transcript
        transcript = hypothesis
        print(transcript)

mycallback = MyRecognizeCallback()
record = "arecord -d 5 -f S16_LE -r 44100 -t wav my_voice.wav"
go = True
while go:
    signal.signal(signal.SIGINT, signal_handler)
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    interrupted = False
    stop_now = False
    print ("Listening for K9 keyword... press Ctrl+C to exit")
    detector.start(detected_callback=K9_detected,
    interrupt_check=stop_snowboy,
    sleep_time=0.03)
    detector.terminate()
    time.sleep(0.1)
    finished = False
    try:
        os.remove("my_voice.wav")
    except OSError:
        pass
    print("Lights on")
    subprocess.call(record, shell=True)
    print ("Lights off")
    with open('my_voice.wav') as f:
        speech_to_text.recognize_with_websocket(audio=f,content_type='audio/l16; rate=44100', recognize_callback=mycallback)
    while not finished:
        time.sleep(0.1)
    response = conversation.message(workspace_id=WAworkspace_id, input={'text':transcript})
    results = re.search(': \{u\'text\': \[u\'(.*)\'\], u\'log', str(response))
    answer = results.group(1)
    answer = './tts ' + answer
    subprocess.call(answer, shell=True)
