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

.service('K9', ['$rootScope','NRInstruction', function($rootScope,NRInstruction) {
    // holds K9 state for all controllers
    // initialisation of service
    //var k9state = {};
    this.main_volt=0;
    this.temp=0;
    this.brain_volt=0;
    this.speed=0;

    this.setStatus = function (status) {
      // set overall dog status based on received object
      // set overall status via series of calls to set function
      // for each element in the array, set that key value pair in k9state
      for (var key in status) {
        if (!status.hasOwnProperty(key)) {
            //The current property is not a direct property of p
            continue;
        }
        // if the keys are toggle switches, use the browser as master
        // until I work out how to stop bad loops happening!
        if (key=="lights" ||
            key=="screen" ||
            key=="eyes" ||
            key=="hover" ||
            key=="motorctrl")
            {
              // the line below is only required if I re-enable this refresh
              // of k9 switch status overriding browser status, but this is
              // only required once I've got the back panel interface working
              if (status[key]==1) {status[key]=true} else {status[key]=false};
            }
        else
        {
           this[key]=status[key];
        }
        this.speed = (Math.abs(this.left) + Math.abs(this.right))/13.7;
        $rootScope.$apply();
      }
    }
    this.toggleValue = function (key,value) {
      // console.log("Key: "+key+" Value: "+value);
      var text;
      var value;
      if (value==true) {text="on";} else {text="off";}
      // console.log("Browser sent "+key+" "+text);
      NRInstruction.send('toggle',key,text);
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
    if ((NRverb == "navigation") && (NRobject != "motorctrl")) {
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

.factory('NodeREDWebSocket', ['$rootScope','msgtoPoint', function($rootScope,msgtoPoint) {
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
            $rootScope.$broadcast("event:k9state",messageObj);
            break;
          case 'collection':
            //console.log("Collection message recognised.");
            messageArray = messageObj.data;
            msgArrayLen = messageArray.length;
            for (var i = 0; i < msgArrayLen; i++){
               sensor = messageArray[i].sensor;
               distance = parseFloat(messageArray[i].distance);
               angle = parseFloat(messageArray[i].angle);
               msgtoPoint.recordReading(sensor,distance,angle);
               console.log(messageArray[i] + " being processed - " + sensor +", "+ distance + ", " + angle );
            }
            break;
          case 'sensor':
            // sensor message has been received
            sensor = messageObj.sensor;
            distance = parseFloat(messageObj.distance);
            // if there is no angle, use the default
            if (isNaN(messageObj.angle)) {
              angle = 1000;
            } else {
              angle = parseFloat(messageObj.angle);
            }
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
    var sensorList = '[{"sensorName":"ultrasonic","x":1200,"y":1200,"angle":999},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":40.0,"max_angle":45.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":35.0,"max_angle":40.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":30.0,"max_angle":35.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":25.0,"max_angle":30.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":20.0,"max_angle":25.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":15.0,"max_angle":20.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":10.0,"max_angle":15.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":5.0,"max_angle":10.0},{"sensorName":"l_ear","x":1158,"y":890,"min_angle":0.0,"max_angle":5.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":355.0,"max_angle":360.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":350.0,"max_angle":355.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":345.0,"max_angle":350.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":340.0,"max_angle":345.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":335.0,"max_angle":340.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":330.0,"max_angle":335.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":325.0,"max_angle":330.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":320.0,"max_angle":325.0},{"sensorName":"r_ear","x":1242,"y":890,"min_angle":315.0,"max_angle":320.0},{"sensorName":"left","x":1125,"y":1306,"angle":90},{"sensorName":"bl_corner","x":1153,"y":1347,"angle":135},{"sensorName":"tail","x":1200,"y":1365,"angle":180},{"sensorName":"br_corner","x":1247,"y":1347,"angle":225},{"sensorName":"right","x":1275,"y":1306,"angle":270}]';
    var sensorLocations = JSON.parse(sensorList);
    var sensorArray = JSON.parse(sensorList);
    // this function returns the current Sensor Array
    this.getSensorArray = function () {
      return sensorArray;
    }
    this.recordReading = function (sensorName, distance, angle) {
      // Receives a sensor reading as natively formatted from the Python controller
      // which means metres and degrees, where the positive x axis
      // is aligned to the forward direction of the dog.
      // It calculates where to plot the sensor reading on the SVG.
      // The SVG is aligned 90 degrees counter clockwise and each
      // point equals 1mm (the overall size is 2.4m x 2.4m)
      //
      var plotPoint = {};
      plotPoint = thisService.sensorPlot (sensorName, distance, angle);
      // store the x, y co-ordinate object in sensorArray
      // this.sensorName.coord = plotPoint
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
      var SVGpoints = 1000 * metres;
      return SVGpoints;
      }
    this.sensorPlot = function (sensorName,distance,angle) {
      // Returns the calculated SVG x,y co-ordinates
      // from the dog oriented distance and angle.
      // The x,y SVG endpoint position is calculated as an offset from
      // a point held in the sensorLocations array which
      // describes in SVG terms where the sensor is.
      //
      // Assign default and safe values to mySensorLocation.  The default
      // is for the angle to be provided by the sensor reading and for the
      // sensor placed at the centre of the dog.
      //
      // console.log("Name:"+sensorName+" Distance:"+distance+" Angle:"+angle);
      var mySensorLocation = {};
      mySensorLocation.name = sensorName;
      mySensorLocation.x = 1200;
      mySensorLocation.y = 1200;
      mySensorLocation.angle = 999;
      // search for matching sensor location and modify the
      // origin point values if a match is found

      for (var i=0, len=sensorLocations.length; i < len; i++)
      {
         if (!sensorLocations[i].angle) {
            // compare the name and angle
            if ((angle > sensorLocations[i].min_angle) && (angle <= sensorLocations[i].max_angle) && (sensorLocations[i].sensorName == mySensorLocation.name)){
               break;
            }
         }
         else {
            if (sensorLocations[i].sensorName == mySensorLocation.name){
               break;
            }
         }
      }
      console.log("Match found - " + sensorLocations[i].sensorName + ":" + i);
      mySensorLocation.x = sensorLocations[i].x;
      mySensorLocation.y = sensorLocations[i].y;
      // angles that are specified as 999 are 'variable' and the value
      // will be supplied inside ihe sensor reading
      // fixed position sensors will be read in from the sensorLocations array
      if (sensorLocations[i].angle)
         {
         mySensorLocation.angle = sensorLocations[i].angle;
         }
      else
         {
         mySensorLocation.angle = angle;
         }
      // the endpoint object is the SVG location to plot the sensor
      // this is calculated using basic trigonometry and scaling
      // using mySensorLocation as the origin point
      var endpoint={};
      endpoint.index = i;
      endpoint.sensor = mySensorLocation.name;
      // calculate x,y offset co-ordinates in dog orientation
      var x_real;
      var y_real;
      // calculate x,y offset based on sensor reading
      // and multiplies by 1,000 to get SVG points
      x_real =  Math.cos(thisService.deg2Rad(mySensorLocation.angle))*thisService.dist2SVG(distance);
      y_real =  Math.sin(thisService.deg2Rad(mySensorLocation.angle))*thisService.dist2SVG(distance);
      // Now convert real x,y co-ordinates to SVG co-ordinates.
      // This is done by rotating the calculated offset
      // by 90 degrees counter clockwise.
      endpoint.x = mySensorLocation.x + Math.round(y_real * -1,0);
      endpoint.y = mySensorLocation.y + Math.round(x_real * -1,0);
      //endpoint.x = Math.round(mySensorLocation.x + ( thisService.dist2SVG(distance) * Math.cos(mySensorLocation.angle)),0);
      //endpoint.y = Math.round(mySensorLocation.y + ( thisService.dist2SVG(distance) * Math.sin(mySensorLocation.angle)),0);
      console.log("endpoint: x:"+endpoint.x+",y:"+endpoint.y);
      return endpoint
      }
}])
