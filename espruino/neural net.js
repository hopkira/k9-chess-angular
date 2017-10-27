/*

Ultrasonic training set generator
for Espruino and Synaptic neural net

Once running, disconnect Espruino from console
and redirect console output to CSV file using:

cat /dev/cu.usbmodemXXXX > filename.csv

Once green light only is lit, close file using CTRL+C

Published under The Unlicense
Richard Hopkins, 7th October 2017

*/

// Define Espruino pins for PWM Servo and Ultrasonic Sensors
var PWM = A7;
var FRONT_LEFT = A2;
var FRONT_RIGHT = A3;
var LEFT = A4;
var RIGHT = A5;
var BACK = A6;
var SERVO = require("servo").connect(PWM);

// Define manual test parameters
var VIEWS = 4;
var VIEW_INCR = 1;
var DISTANCE = 0.33333333; // 1.5m=1, 1m=0.66666667, 0.5m=0.33333333
// Define automated test parameters
var SERVO_WAIT = 250;  // time for servo to move c.250ms
var NUM_READINGS = 50; // number of fine angle increments
var READINGS = 10; // number of readings per position

// Define how long person takes to move transmitter
var HUMAN_WAIT = 10000 + (SERVO_WAIT*NUM_READINGS); // c.10,000ms

var ON = 1;
var OFF = 0;
var start_time = getTime();

// Calculate information about test
var DURATION = (VIEWS/VIEW_INCR)*(HUMAN_WAIT+(SERVO_WAIT*NUM_READINGS))/1000/60;
var TOTAL_READINGS = (VIEWS/VIEW_INCR)*NUM_READINGS*READINGS;

// initialise position of servo and transmitter
var view = 0;
var pwm = 0;

// turn green LED off
digitalWrite(LED2, OFF);

// Dump information about test to console
console.log("Test rig will create " + TOTAL_READINGS +" element training set in roughly " + DURATION + " minutes.");

// Main loop used to enable human tester to move
// transmitter to each of the compass points
function view_loop() {
  if (view < VIEWS) {
    setTimeout(function(){
      pwm = 0 ;
      record_loop(view);
      view_loop();
    },HUMAN_WAIT);
    view = view + VIEW_INCR;
  }
  else {
    // turns green light on for final set of readings
    digitalWrite(LED2, ON);
  }
}

// Inner loop that moves servo from one extreme to the other
function record_loop(actual_view){
  if (pwm <= 1+(1/NUM_READINGS)) {
    setTimeout(function(){
      record_loop(actual_view);
    },SERVO_WAIT);
    take_reading(actual_view, pwm);
    // Position servo
    SERVO.move(pwm,200);
    // Increment servo position
    pwm = pwm + (1/NUM_READINGS);
  }
  else {
    SERVO.move(0,8000); // slowly reset servo if end of loop
  }
}

// Takes reading from sensors and sends it to console
function take_reading(actual_view,actual_pwm){
  // Red LED will flash when readings are being taken
  digitalWrite(LED1, ON);
  for (var read=0; read<READINGS; read++){
    front_left = analogueRead(FRONT_LEFT);
    front_right = analogueRead(FRONT_RIGHT);
    left = analogueRead(LEFT);
    right = analogueRead(RIGHT);
    back = analogueRead(BACK);
    time = Math.round(getTime()-start_time);
    angle = ((actual_view-1)*Math.PI/2) + (actual_pwm*Math.PI/2);
    // calculate values for sine and cosine
    // that are normalized between 0 and 1
    // for injection into the neural net
    sine = (1+Math.sin(angle))/2;
    cosine = (1+Math.cos(angle))/2;
    console.log(
      "{input:[" + front_left + "," + front_right + "," + left + "," + right + "," + back + "],output: [" + sine+"," + cosine + "," + DISTANCE + "]},");
  }
  digitalWrite(LED1, OFF);
}

// Kicks off the test
console.log("var trainingSet = [");
SERVO.move(0,8000);
view_loop(view);
