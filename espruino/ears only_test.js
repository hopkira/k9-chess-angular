/*

Simple espruino program for the ear servos that:
   - moves the ears smoothly backwards and forwards

Published under The Unlicense

Richard Hopkins, 1st October September 2018

*/
var PWM_l = 0; // minimum position for sevo
var PWM_r = 1; // maximum position for servo
var PIN_PWM_l = B15; // left ear PWM pin name
var PIN_PWM_r = B14; // right ear PWM pin name
var move_int=23; // time between servo moves in ms
var num_steps = 22; // number of steps in full sweep
var step = 0; // start at step 0
var direction = 1; // direction of first sweep

// position servo as instructed (from 0 to 1)
// using a pulse between 0.75ms and 2.25ms
function setServo(pin,pos) {
 if (pos<0) pos=0;
 if (pos>1) pos=1;
 //console.log(pos);
 analogWrite(pin, (1+pos) / 50.0, {freq:20});
}

// this function is called automatically on Pico initialisation
// it will move the ears via their servos
function onInit() {
   setInterval(moveEars,move_int);
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

// calculate the next position for the servos and move them to it
function moveEars(){
   step = step + direction;
   if (step > num_steps) {
      direction = -1;
      step = num_steps-1;
   }
   if (step < 0) {
      direction = 1;
      step = 1;
   }
   position = calculateServoPos(step);
   scaled_pos = scaleServoPos(position);
   setServo(PIN_PWM_l,scaled_pos);
   setServo(PIN_PWM_r,1-scaled_pos);
}
