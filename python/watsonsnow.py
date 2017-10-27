#
# K9 Watson and Snowboy
# by Richard Hopkins
#
# Released under The Unlicense License 2017
#
# TTS elements derived from
# Joshua Rees-Jones, IBM intern
# Getting robots to listen
# Conversation elements derived from:
# watson-developer-cloud/python-sdk/examples/conversation_v1.py
# Snowboy elements derived from 
# Kitt-AI/snowboy/examples/Python/demo.py

from ws4py.client.threadedclient import WebSocketClient
from watson_developer_cloud import ConversationV1
import sys, signal, snowboydecoder, re, base64, json, ssl, subprocess, threading, time

# Initialising TTS global variables
speech_received = False # has speech been returned by Watson?
transcript = "silence" # default value for speech if nothing returned

# Initialise snowboy global variables
model = "./K9.pmdl"
interrupted = False

# Initialise conversation global variables
conversation = ConversationV1(username='your conversation username here',password='your conversation password here',version='actual conversation version here')
workspace_id = 'your conversation workspace id here'

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
		username = "your STT username"
		password = "your STT password"
		ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
		auth_string = "%s:%s" % (username, password)
		base64string = base64.encodestring(auth_string).replace("\n", "")
		self.listening = False
		try:
			WebSocketClient.__init__(self, ws_url,headers=[("Authorization", "Basic %s" % base64string)])
			self.connect()
		except: print "Failed to open WebSocket."

	def opened(self):
		self.send('{"action": "start", "content-type": "audio/l16;rate=16000"}')
		self.stream_audio_thread = threading.Thread(target=self.stream_audio)
		self.stream_audio_thread.start()

	def received_message(self, message):
		global speech_received
		global transcript
		message = json.loads(str(message))
		if "state" in message and not speech_received:
			if message["state"] == "listening":
				self.listening = True
		if "results" in message:
			self.listening = False
			speech_received = True
			self.send('{"action": "stop"}')
			results = re.search('transcript\'\: u\'(.*)\'\}\]', str(message))
			if results:
				transcript = results.group(1)
				self.close()
		if "error" in message:
			speech_received = True
			self.listening = False
			self.send('{"action": "stop"}')
			self.close()

	def stream_audio(self):
		while not self.listening:
			time.sleep(0.1)

		reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
		p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)

		while self.listening:
			data = p.stdout.read(1024)
			try:
				self.send(bytearray(data), binary=True)
			except ssl.SSLError: pass

		p.kill()

	def close(self):
		self.listening = False
		speech_received = True
		self.stream_audio_thread.join()

# K9 hotword has been detected
def K9_detected():
	global stop_now
	stop_now = True # get the detector to terminate
	
def speech_to_text():
	global transcript
	global speech_received
	speech_received = False # has speech been returned by Watson?
	transcript = "silence" # default value for speech if nothing returned
	stt_client = SpeechToTextClient()
	while not speech_received:
		time.sleep(0.1)
	return transcript

def stop_snowboy():
	global stop_now
	return stop_now

go = True
while go:
	interrupted = False
	stop_now = False
	detector.start(detected_callback=K9_detected,interrupt_check=stop_snowboy,sleep_time=0.03)
	detector.terminate()
	time.sleep(0.03)
	speech_received = False
	transcript = "silence"
	speech_to_text()
	response = conversation.message(workspace_id=workspace_id, message_input={'text':transcript})
	results = re.search('\], u\'text\': \[u\'(.*)\'\]\}, u\'alt', str(response))
	answer = results.group(1)
	answer = './tts ' + answer
	subprocess.call(answer, shell=True)