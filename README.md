# K9 Controller
Code and configuration files for a chess playing enhancement to a remote presence robot!

The root directory contains some frequently requested design documents and plans as PDFs, plus the index.html that defines the HTML that is the root page of the end user app.

# Directory Structure

## chess
Chess profiler by the amazing Maris Van Sprang!

## conversation
JSON configuration files for IBM Watson Assistant workspaces

## css
CSS files for end user interface largely generated and maintained by Ionic

## espruino
Embedded JavaScript routines that run on Espruino picos to offload the overhead of working with low level sensors from the Pi.  This includes a neural net implementation for combining five ultrasonic sensor readings into a position vector.  

File | Description
---  | ---
moving_avg_net.js | Generated neural net that runs on the Espruino; generates a moving average of readings
back_panel.js | Controller for the back planel IR sensors, switches and touch sensors

## img
Visuals for end user interface, includes default camera image and SVG for Sensors tab.  Some reference images of the hero prop are also included.

## js
The AngularJS JavaScript that is the bulk of the end user application function

File | Description
---  | ---
app.js | Basic structure of the application modules plus some low level functions
controllers.js | Each tab has its own controller in this file that respondes to user events and manipulates the model.  This separation of event handling and model manipulation makes maintenance and problem diagnosis easier.
directives.js | There are custom directives for the locked/unlocked icon on each tab (that shows whether communications between browser and dog are working in both directions) and the joystick on the Motors tab.  These directives make the HTML much easier to understand and maintain.
services.js | The shared services maintain a model of the state of the dog in the front end app; they also support the creation of sockets between the app and dog and the standardisation of messages flowing over that connection.  The translation between sensor readings and the SVG world are also calculated here for display on the sensors page.
  
## node-RED
This directory contains the flows to control K9.  It provides the means to flow information between the various elements of the dog and co-ordinates movement and speech.  It also contains the definition of the dashboard to show on K9's screen.

## python
This directory contains the python programs that use the Adafruit PWM Servo Driver and RoboClaw PID MotorController to make K9 move. A harness is included to generate sensor data to simulare collisions.  There are also some simple scripts to interface to Watson Conversation and STT (and to K9's espeak TTS)

Program | Description
---  | ---
K9PythonController.py | RoboClaw based Motor Controller
ear_controller.py | Controls K9's ears to collect forward facing LIDAR information
logo.py | Translates simple Logo paths into a movement plan for the RoboClaw
memory.py | Provides access to K9's short term memory which stores state and sensor readings
status.py | Sends K9's current state to node-RED (and browser) as JSON string every 200ms
K9_roboclaw_init.py | Stores PID and motor settings in Roboclaw NVRAM
node_RED_harness_ultrasonic.py | Creates simulated LIDAR, IR and ultrasonic sensor readings
ttsrobot.py | Uses Snowboy, Watson STT, Conversation and TTS - a bit Alexa like :+)

## script
Simple deployment scripts to move code into right place on the Pi

## snap
Standard JavaScript library used to integrate SVG and AngularJS on the Sensors page
 
## templates
This directory contains the HTML for each of the tabs of the user interface (including the definition of the tabs themselves!).  Keeping the html for each tab separately simplifies testing and maintenance.

## tessel
Tessel is not currently used on the K9 robot
