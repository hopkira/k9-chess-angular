#
# K9 Conversation by Richard Hopkins using
# Kitt-AI Snowboy for hotword recognition
# Watson Speech to Text (streaming to sockets)
# Watson Conversation
# eSpeak Text to Speech
# Robot status displayed with Adafruit PWM Servo Driver driving LED brightness
#
# TTS elements derived from
# Joshua Rees-Jones, IBM intern
# "Getting robots to listen"
#
# Conversation elements derived from:
# watson-developer-cloud/python-sdk/examples/conversation_v1.py
#
# Snowboy elements derived from
# Kitt-AI/snowboy/examples/Python/demo.py
#

from ws4py.client.threadedclient import WebSocketClient
from watson_developer_cloud import ConversationV1
from Adafruit_PWM_Servo_Driver import PWM
import sys, signal, snowboydecoder, re, base64, json, ssl, subprocess, threading, time

# Initialising TTS global variables
speech_received = False # has speech been returned by Watson?
transcript = "silence"	# default value for speech if nothing returned

# Initialise snowboy global variables
model = "./K9.pmdl"
interrupted = False

# Initialise conversation global variables
conversation = ConversationV1(
    username='xxxxx',
    password='xxxxx',
    version='xxxxx')
workspace_id = 'xxxxxx'

# Initialise the PWM device using the default address
pwm = PWM(0x40)
pwm.setPWMFreq(100)  # Set frequency to 100 Hz

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
class SpeechToTextClient(WebSocketClient):
	def __init__(self):
		username = "xxxxxx"
		password = "xxxxxx"
		ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
		auth_string = "%s:%s" % (username, password)
		base64string = base64.encodestring(auth_string).replace("\n", "")
		self.listening = False
		print "def_init_(self), self.listening = False"
		try:
			WebSocketClient.__init__(self, ws_url,
			headers=[("Authorization", "Basic %s" % base64string)])
			self.connect()
			print "self.connect()"
		except: print "Failed to open WebSocket."
	def opened(self):
		print "opened(self) and self.send"
		self.send('{"action": "start", "content-type": "audio/l16;rate=16000"}')
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
				print "Listening is now true"
		if "results" in message:
			self.listening = False
			speech_received = True
			print "Sending stop transcription message"
			self.send('{"action": "stop"}')
			results = re.search('transcript\'\: u\'(.*)\'\}\]', str(message))
			if results:
				transcript = results.group(1)
				print str(transcript)
			set_PWM(PWM_eye,3)
			self.close()
			print "Speech_received, exiting"
			# self.close()
			# sys.exit()
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
			print "sleeping"
			time.sleep(0.1)
		reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
		print "arecord and p=subprocess.Popen"
		p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
		while self.listening:
			print "while self.listening is true"
			data = p.stdout.read(1024)
			try:
				print "self.send bytearray"
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
		print "not hearing anything, so sleeping"
		time.sleep(0.1)
	return transcript

def stop_snowboy():
	global stop_now
	print "Waiting: " + str(stop_now)
	return stop_now

# Sets brightness of PWM lights from 0 to 100
def set_PWM(light, brightness):
	global pwm
	light = int(light)
	brightness = int(float(brightness)*40.95)
	if light >=0 and light <=15: # check that PWM channel exists
		if brightness >= 0 and brightness <= 4095: # check that frequency is valid
			pwm.setPWM(0,light,brightness)

# Initialise the eye lights at 3%
set_PWM(PWM_eye,3)

go = True
while go:
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
	response = conversation.message(workspace_id=workspace_id, message_input={'text':transcript})
	results = re.search('\], u\'text\': \[u\'(.*)\'\]\}, u\'alt', str(response))
	answer = results.group(1)
	answer = './tts ' + answer
	print str(answer)
	subprocess.call(answer, shell=True)
