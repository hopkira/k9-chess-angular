/*
Simple espruino program for the ear LIDAR sensors that:
   - moves the ears smoothly backwards and forwards
   - sends LIDAR readings via the USB cable to the node-RED on the Pi
   - responds to speed commands from USB serial port

All messages to node-RED are sent as JSON strings terminated in an ! via a
serial connection over a USB cable.

Published under The Unlicense

Richard Hopkins, 9th September 2018
*/
// set up USB connector to send messages to Pi via
// serial over USB
USB.setup(115200,{bytesize:8,stopbits:1});
//LoopbackA.setConsole();
var PWM_l = 0.15; // minimum position for sevo
var PWM_r = 0.8; // maximum position for servo
var PIN_PWM_l = B15; // left ear PWM pin name
var PIN_PWM_r = B14; // right ear PWM pin name
var PIN_LIDARX_l = B4; // pin for LIDAR on/off
var PIN_LIDARX_r = A8; // pin for LIDAR on/off
var PIN_pot_l = B1; // pin for servo potentiometer
var PIN_pot_r = A7; // pin for servo potentiometer
var PIN_sda = B3; // pin for I2C SDA cable
var PIN_scl = B10; // pin for I2C SCL cable
var move_int=1000; // time between servo moves in ms
var scan_int_l=10000; // time between readings in ms on left LIDAR
var scan_int_r=10000; // time between readings in ms on right LIDAR
var num_steps = 50; // number of steps in full sweep
var step = 0; // start at step 0
var direction = 1; // direction of first sweep
var LIDAR_l;  // object for left LIDAR sensor
var LIDAR_r; // object for right LIDAR sensor
var vRef = E.getAnalogVRef(); // voltage reference
var num_readings = 1;  // number of times voltage has been read

// position servo as instructed (from 0 to 1)
// using a pulse between 0.75ms and 2.25ms
function setServo(pin,pos) {
 if (pos<0) pos=0;
 if (pos>1) pos=1;
 //console.log(pos);
 analogWrite(pin, (1+pos) / 50.0, {freq:20});
}

// initialise the LIDAR and I2C interfaces
// turn off the LIDARs and use the I2C 2 bus at 400kHz
function initHW(){
   digitalWrite(PIN_LIDARX_l,0);
   digitalWrite(PIN_LIDARX_r,0);
   I2C2.setup({sda:PIN_sda, scl:PIN_scl, bitrate:100000});
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
   setInterval(takeReading,scan_int_l,'l_ear');
   setInterval(takeReading,scan_int_r,'r_ear');
   USB.on('data', function (data) {
     USB.print(data);
     switch(data) {
       case "stop":
        move_int=1000;
        scan_int_l=1000;
        scan_int_r=1000;
        break;
       case "slow":
        move_int=500;
        scan_int_l=1000;
        scan_int_r=1000;
        break;
      case "medium":
        move_int=50;
        scan_int_l=100;
        scan_int_r=100;
        break;
      case "fast":
        move_int=23;
        scan_int_l=41;
        scan_int_r=43;
        break;
        }
      });
}

// calculate desired servo position based on step
// the trigonometry smooths the movement of the servos
function calculateServoPos(step) {
   // each swing of the ears is separated into a number of steps (num_steps)
   // and the angle is calculated as the fraction of a half circle
   angle = step/num_steps*Math.PI;
   //console.log("Angle: "+String(angle));
   // the position calculated transforms the linear steps into a smoooth
   // natural motion
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
  message = String('{"type":"'+type+'","sensor":"'+sensor+'","distance":"'+distance+'","angle":"'+angle+'"}');
   USB.print(message);
  //console.log(message);
  }

// take a reading from each of the LIDAR sensors
function takeReading(ear){
  var dist;
  var ear_dir;
  if (ear == 'l_ear'){
     read_lidar = LIDAR_l;
     read_pin = PIN_pot_l;
  }
  if (ear == 'r_ear'){
     read_lidar = LIDAR_r;
     read_pin = PIN_pot_r;
  }
  dist = read_lidar.performSingleMeasurement().distance;
  // if distance is less than or equal to 20mm, then report 0mm
  if (dist != 20) {
    ear_dir=analogRead(read_pin)*vRef;
    sendMsg("LIDAR",ear,dist,ear_dir);
  }
}

// calculate the next position for the servos and move them to it
function moveEars(){
   if (move_int > 500) {return;}
   else {
     step = step + direction;
     if (step > num_steps) {
        direction = -1;
        step = num_steps-1;
     }
     if (step < 0) {
        direction = 1;
        step = 1;
     }
     scaled_pos = step_lookup[step];
     setServo(PIN_PWM_l,scaled_pos);
     setServo(PIN_PWM_r,1-scaled_pos);
  }
}

// create an array of all the valid scaled positions
step_lookup = [];
for (step = 0; step <= num_steps; step++) {
  step_lookup[step] = scaleServoPos(calculateServoPos(step));
  //print(step + " : " + step_lookup[step]);
}
step = 0;
