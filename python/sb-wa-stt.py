#
# K9 Conversation by Richard Hopkins using -
#
# Kitt-AI Snowboy for hotword recognition
# Watson Speech to Text (streaming to sockets)
# Watson Assistant for Conversation
# eSpeak Text to Speech
# Robot status displayed with Adafruit PWM Servo Driver driving LED brightness
#
# Snowboy elements derived from
# Kitt-AI/snowboy/examples/Python/demo.py
#
# March 2018
#
# Released under The Unlicense
#

from watson_developer_cloud import ConversationV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback
import Adafruit_PCA9685
import os, sys, signal, snowboydecoder, re, base64, json, ssl, subprocess, threading, time

variables = ['WCpassword','WCusername','WCworkspace','WTTSpassword','WTTSusername']

for variable in variables:
    if variable in os.environ:
        pass
    else:
        print "Please set the environment variable " + variable
        sys.exit(1)

# Initialising TTS global variables
speech_received = False # has speech been returned by Watson?
transcript = "silence"    # default value for speech if nothing returned

# Initialise snowboy global variables
model = "./K9.pmdl"
interrupted = False

# Initialise conversation global variables
conversation = ConversationV1(
    username=os.environ['WCusername'],
    password=os.environ['WCpassword'],
    version='2018-02-16')

workspace_id = os.environ['WCworkspace']

# Initialise the PWM device using the default address
pwm = 0
#pwm = Adafruit_PCA9685.PCA9685()
#pwm.set_pwm_freq(100)  # Set frequency to 100 Hz

# Create names for each PWM channel
PWM_eye = 0
PWM_hover = 1

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

signal.signal(signal.SIGINT, signal_handler)
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)

# Web Socket object for communicating to Watson Developer Cloud
# Test to Speech

# Example using websockets
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        print(transcript)

    def on_connected(self):
        print('Connection was successful')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

    def on_error(self, error):
        print('Error received: {}'.format(error))
        set_PWM(PWM_eye,3)
        speech_received = True
        self.listening = False

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        self.listening = True
        set_PWM(PWM_eye,100)
        print('Service is listening')

    def on_transcription_complete(self):
        set_PWM(PWM_eye,3)
        self.stream_audio_thread.join()
        self.listening = False
        speech_received = True
        print('Transcription completed')

    def on_hypothesis(self, hypothesis):
        print(hypothesis)

    def stream_audio(self):
        print "Waiting for audio..."
        while not self.listening:
            time.sleep(0.1)
        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
        print "Starting to send audio to STT..."
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
        while self.listening:
            data = p.stdout.read(1024)
            try:
                self.send_audio(bytearray(data))
            except ssl.SSLError: pass
        p.kill()
        print "Audio sent."

# K9 hotword has been detected
def K9_detected():
    global pwm
    print "K9 hotword detected...\n"
    set_PWM(PWM_eye,30)
    global stop_now
    stop_now = True # get the detector to terminate

def speech_to_text():
    global transcript
    global speech_received
    speech_received = False # has speech been returned by Watson?
    transcript = "silence"  # default value for speech if nothing returned
    print "Initialising speech to text..."
    # Initialise speech to text global variables
    speech_to_text = SpeechToTextV1(
        username=os.environ['WTTSusername'],
        password=os.environ['WTTSpassword'],
        url='https://stream.watsonplatform.net/speech-to-text/api')
    while not speech_received:
        time.sleep(0.1)
    return transcript

def stop_snowboy():
    global stop_now
    if stop_now = True:
        print "Snowboy stop interrupt."
    return stop_now

# Sets brightness of PWM lights from 0 to 100
def set_PWM(light, brightness):
    global pwm
    light = int(light)
    brightness = int(float(brightness)*40.95)
    if light >=0 and light <=15: # check that PWM channel exists
        if brightness >= 0 and brightness <= 4095: # check that frequency is valid
            #pwm.set_pwm(0,light,brightness)
            print "Eye brightness set to: " + str(brightness)

# Initialise the eye lights at 3%
set_PWM(PWM_eye,3)

go = True
while go:
    interrupted = False
    stop_now = False
    print "Listening for K9 keyword... press Ctrl+C to exit"
    detector.start(detected_callback=K9_detected,
    interrupt_check=stop_snowboy,
    sleep_time=0.03)
    detector.terminate()
    time.sleep(0.03)
    speech_received = False
    transcript = "silence"
    print "Calling speech_to_text"
    speech_to_text()
    print "To conversation: " + transcript
    response = conversation.message(workspace_id=workspace_id, input={'text':transcript})
    results = re.search('\], u\'text\': \[u\'(.*)\'\]\}, u\'alt', str(response))
    answer = results.group(1)
    answer = './tts ' + answer
    print str(answer)
    subprocess.call(answer, shell=True)
