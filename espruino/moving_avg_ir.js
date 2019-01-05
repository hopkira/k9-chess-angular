/*

This simple program calculates the distance to the nearest obstacle
for each of the five IR sensors based on a moving average of readings.

It captures the data from the five ultrasonic sensors
every 25ms and maintains a moving average of their last 10 readings
(a period of 200ms)

Program is designed to run on a Espruino microcontroller.

Published under The Unlicense
Richard Hopkins, 30th December 2018

*/
function voltsToMeters(voltage){
    // convert voltage to metres, ignoring high or low takeSensorReadings
    var dist_v;
    if (voltage < 0.5) {
        dist_v = 1.5;
    }
    else if (voltage > 2.5) {
        dist_v = 0.2;
    }
    else {
        dist_v = (1 / voltage) * 0.68;
    }
    return dist_v;
}

function takeSensorReadings(){
	for (i=0;i<sensors;i++){
		sensor_data[i].make_reading(voltsToMeters(analogRead(sensor_data[i].pin)*3.3));
  }
}

function sendNRMsg(type,sensor,distance,angle) {
  message = String('{"type":"'+type+'","sensor":"'+sensor+'","distance":"'+distance+'","angle":"'+angle+'"}');
  USB.println(message);
  digitalWrite(LED2,toggle=!toggle);
}

function sendXYtoNR(){
	for (i=0;i<sensors;i++){
		var distance = sensor_data[i].mov_avg();
        sendNRMsg("sensor",sensor_data[i].name.toString(),sensor_data[i].mov_avg().toString(),sensor_data[i].angle.toString());
		}
}

function onInit(){
  toggle = true;
  // set up USB serial port
  USB.setup(115200,{
	  bytesize:8,    // How many data bits
	  stopbits:1,    // Number of stop bits to use
	  });
  sensor_data = [];  // initialise sensor array that will hold objects
  // list of sensor names
  sensor_names = ["left","bl_corner","tail","br_corner","right"];
  // list of Espruino pins that correspond to the names
  pins = ["A2","A3","A4","A5","A6"];
  angles = [90,135,180,225,270];  // direction of the sensor
  sensors = sensor_names.length;  // how many sensors do we have?
  readings = 10; // the number here must match the length of the readings array
  /*
  Initialise sensor array objects

  This loop creates an object for each sensor, providing each object with
  name, pin identifier and an empty set of readings

  Two methods are created:

	  mov_avg			calculates the average reading of the sensor object

	  make_reading	adds a new reading to the end of the array and
					removes the oldest reading from the front -
					this means that mov_avg will calculate a moving average
					for that sensor object

  */
  for (i=0;i<sensors;i++){
    sensor_data[i] = {
  	  name: sensor_names[i], // sensor name
  	  pin: pins[i], // sensor pin
      angle: angles[i],
  	  reading: [0,0,0,0,0,0,0,0,0,0], // initialise readings array
  	  mov_avg: function() {
  		  var sum = 0;
  		  for (var j in this.reading) {sum += this.reading[j];}  // calculate array total
  		  return sum/readings;  // return the moving average
  		  },
  	  make_reading: function(value) {
  		  this.reading.push(value);  // push new value onto end of array
  		  this.reading.splice(0,1);  // remove first value from array
  	  }
    }
  ;}
  // take set of sensor readings every 25ms
  var scan=setInterval(takeSensorReadings,25);
  // send message to node-RED every 200ms
  var send=setInterval(sendXYtoNR,200);
}
