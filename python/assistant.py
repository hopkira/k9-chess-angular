import os, sys, subprocess, threading, time, json, re, signal, snowboydecoder,ssl,ast
import requests
from requests.auth import HTTPBasicAuth
from ws4py.client.threadedclient import WebSocketClient
from watson_developer_cloud import ConversationV1
import Adafruit_PCA9685

STTusername = os.environ['WTTSusername']
STTpassword = os.environ['WTTSpassword']
WAusername = os.environ['WCusername']
WApassword = os.environ['WCpassword']
WAworkspace_id = os.environ['WCworkspace']

conversation = ConversationV1(
    username=WAusername,
    password=WApassword,
version='2018-02-16')

print "STT Username: " + str(STTusername)
print "STT Password: " + str(STTpassword)
print "WA Username: " + str(WAusername)
print "WA Password: " + str(WApassword)
print "WA Workspace: " + str(WAworkspace_id)

r = requests.get('https://stream.watsonplatform.net/authorization/api/v1/token?url=https://stream.watsonplatform.net/speech-to-text/api', auth=HTTPBasicAuth(STTusername, STTpassword))
print r.status_code
auth_token = (r.content)

# Initialising TTS global variables
speech_received = False # has speech been returned by Watson?
transcript = "silence"	# default value for speech if nothing returned

# Initialise snowboy global variables
model = "./K9.pmdl"
interrupted = False

# Initialise the PWM device using the default address
#pwm = Adafruit_PCA9685.PCA9685()
#pwm.set_pwm_freq(100)  # Set frequency to 100 Hz
pwm=0

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

class SpeechToTextClient(WebSocketClient):

    def __init__(self):
        ws_url = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'
        self.listening = False
        try:
            WebSocketClient.__init__(self, ws_url,
            headers=[("X-Watson-Authorization-Token",auth_token)])
            self.connect()
        except: print "Failed to open WebSocket."

    def opened(self):
        print "opened(self) and self.send"
        self.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true}')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()
    def received_message(self, message):
        global speech_received
        global transcript
        global pwm
        message = json.loads(str(message))
        print "Received: " + str(message)
        if "state" in message and not speech_received:
            if message["state"] == "listening":
                self.listening = True
                set_PWM(PWM_eye,100)
                print "Speak now..."
        if "results" in message:
            print "Got here!"
            print message['results'][0]['final']
            print message['results'][0]['alternatives'][0]['transcript']
            if message['results'][0]['final'] :
                transcript = message['results'][0]['alternatives'][0]['transcript']
                self.listening = False
                speech_received = True
                print "Sending stop transcription message"
                self.send('{"action": "stop"}')
                set_PWM(PWM_eye,3)
                self.close()
                print "Speech_received, exiting"
        if "error" in message:
            speech_received = True
            self.listening = False
            self.send('{"action": "stop"}')
            print "no speech heard for 30 seconds, exiting"
            set_PWM(PWM_eye,3)
            self.close()

    def stream_audio(self):
        print "Entering stream_audio(self)"
        while not self.listening:
            time.sleep(0.1)
        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
        print "arecord and p=subprocess.Popen"
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
        while self.listening:
            #print "while self.listening is true"
            data = p.stdout.read(1024)
            try:
                #print "self.send bytearray"
                self.send(bytearray(data), binary=True)
            except ssl.SSLError: pass
        p.kill()
        print "p.kill()"

    def close(self):
        self.listening = False
        speech_received = True
        self.stream_audio_thread.join()
        print "close self - self.listening false - clean closure"

# K9 hotword has been detected
def K9_detected():
    global pwm
    print "K9 detected\n"
    set_PWM(PWM_eye,30)
    global stop_now
    stop_now = True # get the detector to terminate

def speech_to_text():
    global transcript
    global speech_received
    speech_received = False # has speech been returned by Watson?
    transcript = "silence"  # default value for speech if nothing returned
    print "stt_client initialisation"
    stt_client = SpeechToTextClient()
    while not speech_received:
        #print "not hearing anything, so sleeping"
        time.sleep(0.1)
    return transcript

def stop_snowboy():
    global stop_now
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


print "Calling listen_for_K9"
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
response = conversation.message(workspace_id=WAworkspace_id, input={'text':transcript})
results = re.search(': \{u\'text\': \[u\'(.*)\'\], u\'log', str(response))
answer = results.group(1)
answer = './tts ' + answer
subprocess.call(answer, shell=True)
