USB.setup(115200,{bytesize:8,stopbits:1,parity:none});
function makeReading() {
 IRSensors();
}

var i = setInterval(makeReading, 60);

function IRSensors() {
  var sensors=[
    {sensorName:"LeftA",pinName:"B1"},
    {sensorName:"LeftB",pinName:"A7"},
    {sensorName:"RightA",pinName:"A6"},
    {sensorName:"RightB",pinName:"A5"}
  ];
  var numSensors=sensors.length;
  for (var sensor=0; sensor < numSensors; sensor++) {
    adcPin= new Pin(sensors[sensor].pinName);
    sensorName = sensors[sensor].sensorName;
    reading = analogRead(adcPin);
    sendMsg("sensor",sensorName,reading);
    }
}

function sendMsg(type,sensor,reading) {
  message = String('{"type":"'+type+'","sensor":"'+sensor+'","reading":"'+reading+'"}\n');
  USB.print(message);
  }
