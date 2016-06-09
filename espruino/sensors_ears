/*
Initialse the state of the dog - should be an init function
*/
var PWM_freq=150; // PWM frequency
var PWM_l = 0.1; // potentiometer reading when ear fully left
var PWM_r = 0.6; // potentiometer reading when ear fully right
var PIN_PWM_l = B15; // left ear PWM pin name
var PIN_PWM_r = B14; // right ear PWM pin name
var scan_int=10; // time between scans in ms
// var time;

/*
Initialise the web socket to talk to node-RED
*/
var IP_K9 = "clockwood.diskstation.me";
var WebSocket = require("ws");
var ws = new WebSocket(IP,K9,{
  port:1880,
  protocolVersion:13,
  origin:'K9Espruino',
  keepAlive:60
  });


// point ears inward
analogWrite(PIN_PWM_l,PWM_r,{freq:PWM_freq}); // position left ear
analogWrite(PIN_PWM_r,PWM_l,{freq:PWM_freq}); // position right ear

// websocket object functions
ws.on('open', function(){
  console.log("Connected to K9 node-RED server");
});

ws.on('close', function() {
  console.log("Connection closed");
});

/*
a function that runs every "scan_int" ms
it performs two functions:

1. it reads the potentiometer voltage of the two
ear servos.
when both ears have passed the end of their travel
the direction of motion of the ears is reversed

2. it reads the IR proximity sensors attatched
to each of the ears and reports back the distance to the nearest obstacle

The combination of the ear voltage and the sensor
voltage are translated into a vector to the nearest
obstacle

*/
var scan = setInterval(function(){
  var l_ear_dir; // reading from left ear potentiometer
  var r_ear_dir; // reading from right ear potentiometer
  var l_ear_IR; // reading from left ear infra-red sensor
  var r_ear_IR; // reading from right ear infra-red sensor
  var pot_l = 0.78; // PWM position for fully left
  var pot_r = 2.35; // PWM position for fully right
  var PIN_pot_l = B1; // left ear potentiometer pin name
  var PIN_pot_r = A7; // right ear potentiometer pin name
  var PIN_IR_l = A6; // left ear IR pin
  var PIN_IR_r = A5; // right ear IR pin
  var message;
  // var time_new;
  var vref=E.getAnalogVRef(); // voltsge reference for Espruino
  l_ear_dir=analogRead(PIN_pot_l)*vref;
  l_ear_IR=analogRead(PIN_IR_l)*vref;
  r_ear_dir=analogRead(PIN_pot_r)*vref;
  r_ear_IR=analogRead(PIN_IR_r)*vref;
  if ((l_ear_dir < pot_l) && (r_ear_dir > pot_r)) {
    analogWrite(PIN_PWM_l,PWM_r,{freq:PWM_freq});
    analogWrite(PIN_PWM_r,PWM_l,{freq:PWM_freq});
    }
  if ((l_ear_dir > pot_r) && (r_ear_dir < pot_l)) {
    analogWrite(PIN_PWM_l,PWM_l,{freq:PWM_freq});
    analogWrite(PIN_PWM_r,PWM_r,{freq:PWM_freq});
    }
  /*
  time_new = getTime();
  elapsed = time_new - time;
  time = time_new;
  console.log(elapsed*1000,ear_direction);
  */
  message = '{reading:[{"type":"ear","source":"left","direction":' + l_ear_dir + ',"reading":' + l_ear_IR + '},{"type":"ear","source":"right","direction":' + r_ear_dir + ',"reading":' + r_ear_IR + '}]}';
  //ws.send(message);
  console.log(message);
},scan_int);