// K9 Motor Encoder

USB.setup(115200,{bytesize:8,stopbits:1,parity:none});

// The number of phase transistions since last poll
// for Left and Right wheels
var Lclicks = 0, Rclicks = 0;
// Values from each of the four sensors
// Left, Right and Track A and B
var LtrA = 0, LtrB = 0, RtrA = 0, RtrB = 0;
// Stored values from the Track A sensors
var oldLtrA = 0, oldRtrA = 0;
var count = 0;

function sendSpeed(){
  //
  // 4mph = 1.8m/s
  //      = 4 rev/s or 48 clicks/s
  //
  // Wheel circumference = 0.44m
  // 12 clicks = 1 revolution
  // 1 m/s = 2.237 mph
  //
  message = String('{"type":"encoder","sensor":"IR","left":"'+Lclicks+'","right":"'+Rclicks+'"}\n');
  USB.print(message);
  // reset counters
  Lclicks = 0;
  Rclicks = 0;
}

function checkforClick()
{
  // Detect phase transition and increment or
  //decrement wheel clicks depending upon value
  // of other sensor
  if (analogRead(B1)>0.9) {LtrA=1;} else {LtrA=0;}
  if (analogRead(A7)>0.9) {LtrB=1;} else {LtrB=0;}
  if ((oldLtrA == 0) && (LtrA == 1))
      {
      if (LtrB == 1){Lclicks++;} else {Lclicks--;}
      }
  oldLtrA = LtrA;
  // Read right hand sensors
  if (analogRead(A6)>0.9) {RtrA=1;} else {RtrA=0;}
  if (analogRead(A5)>0.9) {RtrB=1;} else {RtrB=0;}
  if ((oldRtrA == 0) && (RtrA == 1))
    {
    if (RtrB == 0){Rclicks++;} else {Rclicks--;}
    }
  oldRtrA = RtrA;
}

// Send measurements to the Pi every 1/10th second
var r = setInterval(sendSpeed, 100);

// Check for a click every two ms
var i = setInterval(checkforClick,2);
