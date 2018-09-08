/*
Simple espruino program for the ear LIDAR sensors that:
   - moves the ears smoothly backwards and forwards
   - sends LIDAR readings via the USB cable to the node-RED on the Pi

All messages to node-RED are sent as JSON strings terminated in an ! via a
serial connection over a USB cable.

Published under The Unlicense

Richard Hopkins, 8th September 2018
*/
// set up USB connector to send messages to Pi via
// serial over USB
//USB.setup(115200,{bytesize:8,stopbits:1});
var PWM_l = 0; // minimum position for sevo
var PWM_r = 1; // maximum position for servo
var PIN_PWM_l = B15; // left ear PWM pin name
var PIN_PWM_r = B14; // right ear PWM pin name
var PIN_LIDARX_l = B4; // pin for LIDAR on/off
var PIN_LIDARX_r = A8; // pin for LIDAR on/off
var PIN_pot_l = B1; // pin for servo potentiometer
var PIN_pot_r = A7; // pin for servo potentiometer
var PIN_sda = B3; // pin for I2C SDA cable
var PIN_scl = B10; // pin for I2C SCL cable
var move_int=10; // time between servo moves in ms
var scan_int=35; // time between readings in ms
var num_steps = 30; // number of steps in full sweep
var step = 0; // start at step 0
var direction = 1; // direction of first sweep
var LIDAR_l;  // object for left LIDAR sensor
var LIDAR_r; // object for right LIDAR sensor
var vRef = E.getAnalogVRef(); // voltage reference
var num_readings = 1;  // number of times voltage has been read

// position servo as instructed between 0 and 1
function setServo(pin,pos) {
 if (pos<0) pos=0;
 if (pos>1) pos=1;
 analogWrite(pin, (1+pos) / 50.0, {freq:20});
}

// initialise the LIDAR and I2C interfaces
// turn off the LIDARs and use the I2C 2 bus at 400kHz
function initHW(){
   digitalWrite(PIN_LIDARX_l,0);
   digitalWrite(PIN_LIDARX_r,0);
   I2C2.setup({sda:PIN_sda, scl:PIN_scl, bitrate:400000});
  console.log("HW init done");
}

// create the LIDAR objects on the I2C bus
function initLIDAR(){
   digitalWrite(PIN_LIDARX_l,1);
   LIDAR_l = require("VL53L0X").connect(I2C2,{address:0x54});
   digitalWrite(PIN_LIDARX_r,1);
   LIDAR_r = require("VL53L0X").connect(I2C2,{address:0x56});
}

// maintain an average vRef number
function refine_vRef(){
  num_readings = num_readings + 1;
  reading = E.getAnalogVRef();
  vRef = (vRef * (num_readings-1)/num_readings) + (reading/num_readings);
  //console.log("Vref: " + vRef);
}

// this function is called automatically on Pico initialisation
// it will initise the I2C bus and the LIDAR and then enable three
// fuctions to run at intervals.  This includes:
// - refining the voltage reference for the board
// - moving the ears via their servos
// - taking a LIDAR reading
function onInit() {
   initHW();
   initLIDAR();
   setInterval(refine_vRef,1000);
   setInterval(moveEars,move_int);
   setInterval(takeReading,scan_int);
}

// calculate desired servo position based on step
// the trigonometry smooths the movement of the servos
function calculateServoPos(step) {
   angle = step/num_steps*Math.PI;
   //console.log("Angle: "+String(angle));
   position = (angle-(Math.cos(angle)*Math.sin(angle)))/Math.PI;
   //console.log("Pos: "+String(position));
   return position;
}

// translates the relative position to an absolute one
// this allows the movement of the ears to be constrained
// if necessary
function scaleServoPos(position) {
   scaled_pos = PWM_l + ((PWM_r-PWM_l)*position);
   //console.log("Pos: "+String(scaled_pos));
   return scaled_pos;
}

// send a JSON message to the Rapsberry Pi via a USB serial connection
function sendMsg(type,sensor,distance,angle) {
  message = String('{"type":"'+type+'","sensor":"'+sensor+'","distance":"'+distance+'","angle":"'+angle+'"}!');
  //USB.print(message);
  console.log(message);
  }

// take a reading from each of the LIDAR sensors
function takeReading(){
   var dist_l = 0;
   var dist_r = 0;
   //var dist_l = LIDAR_l.performSingleMeasurement().distance;
   var l_ear_dir=analogRead(PIN_pot_l)*vRef;
   //var dist_r = LIDAR_r.performSingleMeasurement().distance;
   var r_ear_dir=analogRead(PIN_pot_r)*vRef;
   sendMsg("LIDAR","l_ear",dist_l,l_ear_dir);
   sendMsg("LIDAR","r_ear",dist_r,r_ear_dir);
}

// calculate the next position for the servos and move them to it
function moveEars(){
   step = step + direction;
   if (step > num_steps) {
      direction = -1;
      step = num_steps;
   }
   if (step < 0) {
      direction = 1;
      step = 0;
   }
   position = calculateServoPos(step);
   scaled_pos = scaleServoPos(position);
   setServo(PIN_PWM_l,scaled_pos);
   setServo(PIN_PWM_r,1-scaled_pos);
}
