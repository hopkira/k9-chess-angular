# K9 Assistant Functionality 

Prevously K9 simply used Watson Assistant (aka Conversation) to hold down a simple conversation face to face.  This new configuration uses the same base, but builds on it in two key ways:
* User interaction is also now possible via Slack via a K9 bot (though of course face to face with the robot works just as well)
* K9 can enquire on what actions are outstanding the end user on Github/Zenhub; this is a bit clumsy at the moment and will need some refinement, but the basic connections are there and working.

| file name | descrption |
|---|---|
| __main__.py |is the Cloud Function itself written in Python 3 |
| dialogue.json | is JSON definition of a dialogue that talks to the __main__.py function |
| requirments.txt | is used build the Docker image that includes PyGithHub |
| skill-k9controller.json | incorporates the dialogue file able and defines the skills for the K9 assistant |
