/*

Simple espruino program for the ear servos that:
   - moves the ears smoothly backwards and forwards

Published under The Unlicense

Richard Hopkins, 1st October September 2018

*/
var PIN_PWM_l = B15; // left ear PWM pin name
var PIN_PWM_r = B14; // right ear PWM pin name
var move_int=23; // time between servo moves in ms
var num_steps = 22; // number of steps in full sweep
var step = 0; // start at step 0
var direction = 1; // direction of first sweep
var position = []; // array of position values

// position servo as instructed (from 0 to 1)
// using a pulse between 1ms and 2ms
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
   ear_pos = position[step];
   setServo(PIN_PWM_l,ear_pos);
   setServo(PIN_PWM_r,1-ear_pos);
}

// calculate an array of servo positions
for (n=0; n<=num_steps;n++) {
   angle = n/num_steps*Math.PI;
   position[n] = (angle-(Math.cos(angle)*Math.sin(angle)))/Math.PI;
}

// start ears moving
onInit();

// save state of Espruino
save()
