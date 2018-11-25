function sendMsg(message) {
  messageStr = JSON.stringify(message);
  USB.write(messageStr);
}

function fakeSensor(){
  message = {type:"none",sensor:"none",distance:0,angle:0};
  sendMsg(message);
}

function onInit() {
  setTimeout(function() { Serial1.setConsole(); }, 30000); // give time for Pi to boot and make USB connection
  USB.setup(115200,{bytesize:8,stopbits:1});
  USB.on('data', function (data) {
  message = {type:"response",sensor:"data",distance:data,angle:data};
    sendMsg(message);
  });
  setInterval(fakeSensor,10000);
}
