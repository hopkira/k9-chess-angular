/*

Ultrasonic training set generator
for Espruino and Synaptic neural net

Will direct output to /dev/ttyESPFollow

Published under The Unlicense
Richard Hopkins, 2nd February 2020

*/

// Define Espruino pins for PWM Servo and Ultrasonic Sensors
var FRONT_LEFT = A2;
var FRONT_RIGHT = A3;
var LEFT = A4;
var RIGHT = A5;
var BACK = A6;

var ON = 1;
var OFF = 0;

function makeReading() {
    digitalWrite(LED1, ON);
    front_left = analogRead(FRONT_LEFT);
    front_right = analogRead(FRONT_RIGHT);
    left = analogRead(LEFT);
    right = analogRead(RIGHT);
    back = analogRead(BACK);
    USB.print(
      "input:[" + 
        front_left + "," + 
        front_right + "," + 
        left + "," + 
        right + "," + 
        back + "]");
    digitalWrite(LED1, OFF);
    }

function onInit(){
  setInterval(makeReading,50);
}