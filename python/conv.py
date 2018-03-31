from __future__ import print_function
from watson_developer_cloud import ConversationV1

import os, sys, subprocess, threading, time, json, re

WAusername = os.environ['WCusername']
WApassword = os.environ['WCpassword']

conversation = ConversationV1(
    username=WAusername,
    password=WApassword,
version='2018-02-16')

WAworkspace_id = os.environ['WCworkspace']

print ("WA Username: " + str(WAusername))
print ("WA Password: " + str(WApassword))
print ("WA Workspace: " + str(WAworkspace_id))

transcript = "what is your purpose"

response = conversation.message(workspace_id=WAworkspace_id, input={'text':transcript})

print(response)

results = re.search(': \{u\'text\': \[u\'(.*)\'\], u\'log', str(response))

print(results)

answer = results.group(1)
answer = './tts ' + answer
print (str(answer))
subprocess.call(answer, shell=True)
