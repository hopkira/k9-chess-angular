angular.module('K9.services', [])

/*
.service('K9Controller', ['$rootScope', function($rootScope) {
    // holds K9 state for all controllers
    // initialisation of service
    var k9state = {};
    this.setValue = function (key, value) {
        var oldValue = this.getValue(key);
        k9state[key]=value;
        $rootScope.$apply();
        console.log("K9Controller "+key+", "+value);
    }
    this.getValue = function (key) {
      // get individual dog state based on key
      return k9state[key]||null;
    }
    this.setStatus = function (status) {
      // set overall dog status based on received object
      // set overall status via series of calls to set function
      // for each element in the array, set that key value pair in k9state
      console.log("Updating K9 status");
      for (var key in status) {
        if (!status.hasOwnProperty(key)) {
            //The current property is not a direct property of p
            continue;
        }
        this.setValue(key,status[key]);
      }
    }
    this.getStatus = function () {
      // get overall dog status as an object
      console.log("*** Someone called getStatus");
      return k9state;
    }
    this.position = function () {
      // get position as an object
      var position = {};
      position.l = this.getValue("left");
      console.log("Position obj:"+position.l+" K9 Controller:"+this.getValue("left"));
      position.r = this.getValue("right");
      return position;
      }
}])
*/

.service('K9', ['$rootScope', function($rootScope) {
    // holds K9 state for all controllers
    // initialisation of service
    //var k9state = {};
    this.setStatus = function (status) {
      // set overall dog status based on received object
      // set overall status via series of calls to set function
      // for each element in the array, set that key value pair in k9state
      for (var key in status) {
        if (!status.hasOwnProperty(key)) {
            //The current property is not a direct property of p
            continue;
        }
        if (key=="lights" ||
            key=="screen" ||
            key=="screen" ||
            key=="hover") {
              if (status[key]==1) {status[key]=true} else {status[key]=false};
            }
        this[key]=status[key];
        $rootScope.$apply();
      }
    }
    this.setValue = function (key, value) {
      this[key]=value;
      $rootScope.$apply();
    }
}])

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
    // console.log(message);
  }
}])

.factory('NodeREDWebSocket', ['$rootScope','K9','msgtoPoint', function($rootScope,K9,msgtoPoint) {
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
      // console.log("Received a message " + message)
      listener(message);
        };
    ws.onclose = function(message) {
      console.log("Browser to node-RED socket command circuit closed");
        };
    function listener(message) {
      var messageStr=message.data;
      messageStr=messageStr.replace(/!/g,'');
      var messageObj={};
      messageObj=JSON.parse(messageStr);
      // console.log("Received data from websocket: ",messageObj);
      switch(messageObj.type){
          case 'status':
            if ($rootScope.icon=="button button-assertive icon-left ion-unlocked") {
            $rootScope.icon="button button-balanced icon-left ion-locked";
            console.log("Message received, so connection established");
            $rootScope.$apply();
            }
            // status heartbeat received from Python controller via node-RED
            // reset browser timeout to one second in the future
            clearTimeout($rootScope.timeout);
            $rootScope.timeout=setTimeout(function() {NodeREDWebSocket.timeout();},1500);
            // ensure the various switches are set to their correct value if transmitted
            // "type":"status","command":"update","left": left,"right": right,"lights": lights,"eyes": eyes
            // console.log("Status message received")
            K9.setStatus(messageObj);
            break;
          case 'sensor':
            // sensor message has been received
            sensor = messageObj.sensor;
            distance = parseFloat(messageObj.distance);
            angle=parseInt(messageObj.angle);
            //console.log("NRWSservice: sensor " + sensor + " reports obstruction " + String(distance) + "m away at " + String(angle) + " degrees.");
            // record the sensor reading via the sensorArray service
            msgtoPoint.recordReading(sensor,distance,angle);
            break;
          default:
              // message not recongised
              console.log("Message not recognised");
        }
        };
    NodeREDWebSocket.sendmsg = function(message) {
      // console.log('Sending message', message);
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
    if (NRSettings.dir=="") {filler="";} else {filler="/";}
    var NRwebsocket = "ws://"+ NRSettings.URL +":" + NRSettings.port + filler + NRSettings.dir +"/ws/k9";
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
    // console.log($rootScope.icon);
    return NRconnected;
  }
  this.timeout = function(){
  }
}])

.service('msgtoPoint', ['$rootScope', function($rootScope) {
    // holds K9 sensorArray state
    // initialisation of service
    var thisService=this;
    var sensorList = '[{"sensorName":"leftear","x": 306,"y":452,"angle":999},{"sensorName":"rightear","x": 335,"y":452,"angle":999},{"sensorName":"front","x": 320,"y":463,"angle":90},{"sensorName":"back1","x": 291,"y":593,"angle":180},{"sensorName":"back6","x": 350,"y":593,"angle":360},{"sensorName":"back2","x": 298,"y":612,"angle":216},{"sensorName":"back5","x": 346,"y":612,"angle":324},{"sensorName":"back3","x": 310,"y":620,"angle":252},{"sensorName":"back4","x": 333,"y":620,"angle":288},{"sensorName":"back","x": 320,"y":740,"angle":270}]';
    var sensorLocations = JSON.parse(sensorList);
    var sensorArray = JSON.parse(sensorList);
    // function called as a result of receiving a sensor type message
    this.getSensorArray = function () {
      return sensorArray;
    }
    this.recordReading = function (sensorName, distance, angle) {
      // calculate where to plot the sensor reading on the SVG
      //console.log("sA.rR parameters: " + sensorName +", "+distance+", "+angle);
      var plotPoint = {};
      plotPoint = thisService.sensorPlot (sensorName, distance, angle);
      // store the x, y co-ordinate object in sensorArray
      // this.sensorName.coord = plotPoint;
      // the below line may be necessary but SVG will refresh its own
      // view and hopefully take the latest data...
      // $rootScope.$apply();
      //console.log("sA.rR point: " + JSON.stringify(plotPoint));
      sensorArray[plotPoint.index].x = plotPoint.x;
      sensorArray[plotPoint.index].y = plotPoint.y;
      //console.log("Sensor array: " + JSON.stringify(sensorArray));
      }
    this.deg2Rad = function (degrees) {
      // convert degrees into radians
      var radians;
      radians = degrees * Math.PI / 180;
      return radians;
      }
    this.dist2SVG = function (metres) {
      // convert distance in metres to SVG
      // points
      var SVGpoints = 190 * metres;
      return SVGpoints;
      }
    this.sensorPlot = function (sensorName,distance,angle) {
      // positions are determined using Adobe Illustrator
      // angles are determined using trigonometry; zero degrees
      // is along the x axis, measured anticlockwise
      // degrees are used rather than radians to assist with
      // comprehension
      //
      // Assign default and safe values to mySensorLocation
      var mySensorLocation = {};
      mySensorLocation.name = sensorName;
      mySensorLocation.x = 320;
      mySensorLocation.y = 568;
      mySensorLocation.angle = 999;
      // search for matching sensor location and modify values if
      // a match is found
      for (var i=0, len=sensorLocations.length; i < len; i++) {
        //console.log("Comparing "+sensorLocations[i].sensorName+" with "+mySensorLocation.name);
        if (sensorLocations[i].sensorName == mySensorLocation.name)
          {
          //console.log("Match found - item " + i);
          mySensorLocation.x = sensorLocations[i].x;
          mySensorLocation.y = sensorLocations[i].y;
          // angles that are specified as 999 are 'variable' and the value
          // will be supplied inside ihe sensor reading
          // fixed position sensors will be read in from the sensorLocations array
          if (sensorLocations[i].angle != 999) {
            mySensorLocation.angle = sensorLocations[i].angle;
          }
          else
          {
            mySensorLocation.angle = angle;
          }
        break;
        }
      }
      //console.log("sP result: " + mySensorLocation.name + " - x:" + mySensorLocation.x +" y:" + mySensorLocation.y+" angle:" + mySensorLocation.angle);
      // the endpoint object is the SVG location to plot the sensor
      // this is calculated using basic trigonometry and scaling
      // dist2SVG is used to scale the result from real world metres to SVG points
      // degtoRad converts the angle in degrees to radians to enable the x and y
      // components to be calculated
      var endpoint={};
      endpoint.index = i;
      endpoint.sensor = mySensorLocation.name;
      endpoint.x = Math.round(mySensorLocation.x + ( thisService.dist2SVG(distance) * (Math.cos(thisService.deg2Rad(mySensorLocation.angle)))),0);
      endpoint.y = Math.round(mySensorLocation.y - ( thisService.dist2SVG(distance) * (Math.sin(thisService.deg2Rad(mySensorLocation.angle)))),0);
      return endpoint
      }
}])
