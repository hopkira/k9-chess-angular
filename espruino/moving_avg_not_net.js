/*

This simple program captures the data from the five ultrasonic sensors
every 6ms and maintains a moving average of their last 20 readings
(a period of 120ms).

Program is designed to runs on Espruino microcontroller.

It is designed to provide training data for a neural net and replicates
how data will be fed into that neural net to create a vector to the
ultrasonic transmitter.

Published under The Unlicense
Richard Hopkins, 24th March 2018

*/

function takeSensorReadings(){
	for (i=0;i<sensors;i++){
		sensor_data[i].make_reading(analogRead(sensor_data[i].pin));
		}
}

function sendDatatoPython(){
    var message = "";
	for (i=0;i<sensors;i++){
        message = message + '"' + sensor_data[i].name + '":' + string(sensor_data[i].mov_avg())
        if (i<(sensors-1)) {
            message = message + ",";
        }
    }
    USB.println(message);
}

function onInit(){
  // set up USB serial port
  USB.setup(115200,{
	  bytesize:8,    // How many data bits
	  stopbits:1,    // Number of stop bits to use
	  });
  sensor_data = [];  // initialise sensor array that will hold objects
  // list of sensor names
  sensor_names = ["front_left","front_right","left","right","back"];
  // list of Espruino pins that correspond to the names
  pins = ["A2","A3","A4","A5","A6"];
  sensors = sensor_names.length;  // how many sensors do we have?
  readings = 20; // the number here must match the length of the readings array
  /*
  Initialise sensor array objects

  This loop creates an object for each sensor, providing each object with
  name, pin identifier and an empty set of readings

  Two methods are created:

	  mov_avg		calculates the average reading of the sensor object

	  make_reading	adds a new reading to the end of the array and
					removes the oldest reading from the front -
					this means that mov_avg will calculate a moving average
					for that sensor object

  */
  for (i=0;i<sensors;i++){
    sensor_data[i] = {
  	  name: sensor_names[i], // sensor name
  	  pin: pins[i], // sensor pin
  	  reading: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], // initialise readings array
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
  // take sensor readings every 6ms
  var scan=setInterval(takeSensorReadings,6);
  // send message to node-RED every 120ms
  var send=setInterval(sendDatatoPython,120);
}
