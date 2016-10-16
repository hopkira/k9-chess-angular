# K9 Chess
Code and configuration files for a chess playing enhancement to a remote presence robot

# Directory Structure

## node-RED
This directory contains the flows to control K9

## python
This directory contains the python programs that use the Adafruit PWM Servo Driver to make K9 move.

Program | Description
---  | ---
servocontroller.py | Manipulates K9s steering and motors with failsafe reliant upon heartbeat
scanning.py | Controls K9s ears
head_down.py | Moves head to down position
head_up.py | Moves head to up position
wag_h.py | Wags tail horizontally
wag_v.py | Wags tail verticslly
servotuner.py | Can drive any PWM servo to any value (for callibration)
tail_up.py | Moves tail to up position
tail_down.py | Moves tail to down position

## www
This directory contains the HTML, CSS and JavaScript files used to provide the K9 user interface.

Directory | Description
---  | ---
k9.html | JQuery Mobile HTML5 pages for user interface
k9stage1.js | JavaScript program that captures user events and passes them and a control heartbeat to node-RED
jquery | Supporting JavaScript libraries
themes | Custom JQuery Mobile CSS Theme for K9

## PiAUISuite modified files

These are new or modified versions of files for Steve Hickson’s
Voicecommand v3 for Raspberry Pi.

File | Description
---  | ---
chat | The new chat file enables K9 to enter into a conversation using Pandorabots.
tts | The modified tts file means that K9 uses male computer generated voice rather than the female Google version used by Voicecommand.
urlencode | The urlencode script enables reserved characters to be passed to the Padorabots web service.

## Pandorabots Personality Files

The files in the files directory define the on-line behaviour of the K9 Pandorabot.  The K9 files are based on Rosie, which is a fork of the ALICE2 brain.  The Pandorabot CLI can be used to upload the brain to your own Pandorabots instance.