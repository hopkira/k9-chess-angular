angular.module('K9.services', [])

.service('K9Controller', function(NRInstruction) {
    // holds K9 state for all controllers
    // initialisation of service
    var k9state = {};
    this.set = function (key, value) {
      // set value in K9 object
      k9state[key]=value;
      // send command to node-RED
      NRInstruction.send('servo',key,value);
      // var message = '{"type":"servo", "object":"'+ key +'", "value":"'+ value +'"}';
      // console.log(message);
      // ws.send(message);
    }
    this.get = function (key) {
      // get individual dog state based on key
      var value = k9state[key];
      return value;
    }
    this.setStatus = function (status) {
      // set overall dog status based on received object
      // set overall status via series of calls to set function
      // for each element in the array, set that key value pair in k9state
      for (var key in status) {
        if (!status.hasOwnProperty(key)) {
        //The current property is not a direct property of p
        continue;
        }
        k9state[key]=status[key];
        console.log("key:" + key + ", value:" + value);
      }
    }
    this.getStatus = function () {
      // get overall dog status as an object
      return k9state;
    }
})

.service('NRInstruction', ['NodeREDWebSocket' ,function(NodeREDWebSocket) {
  // sends Node-RED instruction to Node Red websocket
  this.send = function (verb, object, status) {
    var NRverb = verb;
    var NRobject = object;
    var NRstatus = status;
    var slot1="object";
    var slot2="value";
    if (NRverb=="navigation") {
        NRobject = "motors";
        NRstatus = object;
        NRstatus2 = status;
        slot2="steering";
        slot3="motorspeed";
        var message = '{"type":"' + NRverb + '", "' + slot1 + '": "' + NRobject + '", "' + slot2 + '": "' + NRstatus + '", "' + slot3 + '": "' + NRstatus2 + '"}'; 
        }

    else {
        var message = '{"type":"' + NRverb + '", "' + slot1 + '": "' + NRobject + '", "' + slot2 + '": "' + NRstatus + '"}';    
        }
      
      try {
      NodeREDWebSocket.sendmsg(message);
    }
    catch(err) {
      alert("Not connected to K9 please check the settings");
    }
    console.log(message);
  }
}])

.factory('NodeREDWebSocket', ['$rootScope', function($rootScope) {
    // returns a Web Socket to send instructions over
    var NodeREDWebSocket = function(destinationURL) {
    ws = new WebSocket(destinationURL);
    ws.onopen = function(){
      console.log("Browser to node-RED socket command circuit established");
      ws.send('{"type":"information", "command":"Browser to node-RED socket command circuit established"}');
      // Send alive message to node-RED server to be passed through to Python
      // controller
      setInterval(function () {NodeREDWebSocket.alive();},200);
      $rootScope.timeout=setTimeout(function() {NodeREDWebSocket.timeout();},10000);
        };
    ws.onmessage = function(message) {
      console.log("Reveived a message " + message)
      listener(message);
        };
    ws.onclose = function(message) {
      console.log("Browser to node-RED socket command circuit closed");
        };
    function listener(message) {
      var messageObj = message.data;
      console.log("Received data from websocket: ", messageObj);
      $rootScope.icon="button button-balanced icon-left ion-locked";
      console.log("Message received, so connection established");
      $rootScope.$apply();
      clearTimeout($rootScope.timeout);
      $rootScope.timeout=setTimeout(function() {NodeREDWebSocket.timeout();},1000);
        };
    NodeREDWebSocket.sendmsg = function(message) {
      console.log('Sending message', message);
      ws.send(message);
        };
    NodeREDWebSocket.alive = function() {
        var message = '{"type":"navigation","object":"browser","value":"alive"}';
        NodeREDWebSocket.sendmsg(message);
        }
    NodeREDWebSocket.timeout = function() {
      $rootScope.icon="button button-assertive icon-left ion-unlocked";
      console.log("Message timeout, connection lost");
      $rootScope.$apply();
    }
    }
    return NodeREDWebSocket;
}])

.service('NodeREDConnection', ['$rootScope', 'NodeREDWebSocket', function ($rootScope, NodeREDWebSocket) {
  // captures and stores the details of the Node-RED server
  $rootScope.icon="button button-assertive icon-left ion-unlocked";
  this.saveSettings = function (settings) {
  // saves connection details to local storage
    var NRSettings = {};
    console.log("NodeREDConnection Service - saving settings...");
    NRSettings = settings;
    window.localStorage.setItem("NRURL", NRSettings.URL);
    window.localStorage.setItem("NRdir", NRSettings.dir);
    window.localStorage.setItem("NRport", String(NRSettings.port));
    window.localStorage.setItem("NRpassword", NRSettings.password);
    console.log("NodeREDConnection Service - I stored in local:");
    console.log(NRSettings.URL);
    console.log(NRSettings.dir);
    console.log(NRSettings.port);
    console.log(NRSettings.password);
  }
  this.getSettings = function () {
    // retrieve settings from localStorage
    var NRSettings = {};
    NRSettings.URL = window.localStorage.getItem("NRURL");
    NRSettings.dir = window.localStorage.getItem("NRdir");
    NRSettings.port = parseInt(window.localStorage.getItem("NRport"));
    NRSettings.password = window.localStorage.getItem("NRpassword");
    console.log("NodeREDConnection Service - I retrieved from local:");
    console.log(NRSettings.URL);
    console.log(NRSettings.dir);
    console.log(NRSettings.port);
    console.log(NRSettings.password);
    return NRSettings;
  }
  this.connect = function (settings){
    // connect WebSocket to node-RED as specified
    var NRSettings = {};
    NRSettings = settings;
    var NRwebsocket = "ws://"+ NRSettings.URL +":" + NRSettings.port +"/"+ NRSettings.dir +"/ws/k9";
    console.log("Connecting to " + NRwebsocket);
    // connect to node-RED
    // connect(NRwebsocket);
    new NodeREDWebSocket(NRwebsocket);
  }
  this.disconnect = function() {
    // disconnect ws
    $rootScope.icon="button button-assertive icon-left ion-unlocked";
    console.log("Root scope icon value set to unlocked");
  }
  this.status = function(){
    // determine connection status
    var NRconnected = $rootScope.icon;
    console.log($rootScope.icon);
    return NRconnected;
  }
  this.timeout = function(){
  }
}])

.service('K9SensorController', function() {
    // holds sensor state for display in an array
    // array used to limit amount of state held
    var sensorSlot = 0;
    var sensorReadings = [];
    this.addReading = function (reading) {
    // add reading to current slot and increment slot by one
    }
    this.getReadings = function () {
    return sensorReadings;
    }
});
