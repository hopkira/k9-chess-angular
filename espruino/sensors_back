USB.setup(115200,{bytesize:8,stopbits:1,parity:none});
function makeReading() {
 on = !on;
 digitalWrite(LED1, on);
 IRSensors();
}

var i = setInterval(makeReading, 200);

function IRSensors() {
  var sensors=[
    {sensorName:"back1",pinName:"B1"},
    {sensorName:"back2",pinName:"A7"},
    {sensorName:"back3",pinName:"A6"},
    {sensorName:"back4",pinName:"A5"}
  ];
  var numSensors=sensors.length;
  for (var sensor=0; sensor < numSensors; sensor++) {
    adcPin= new Pin(sensors[sensor].pinName);
    sensorName = sensors[sensor].sensorName;
    reading = analogRead(adcPin);
    distance = convertPin2m(reading);
    sendMsg("sensor",sensorName,distance,999);
    }
}

function sendMsg(type,sensor,distance,angle) {
  message = String('{"type":"'+type+'","sensor":"'+sensor+'","distance":"'+distance+'","angle":"'+angle+'"}!');
  USB.print(message);
  }

function convertPin2m(pinreading) {
  var volts = pinreading * 3.3;
  var m = 1/volts*0.65;
  if (m>1.5){m=1.5;}
  if (m<0.2){m=0.2;}
  return m;
}