angular.module('K9.controllers', [])

// Controller for K9 Motor Tab
.controller('MotorCtrl',["$scope","K9","NRInstruction", function($scope, K9, NRInstruction) {
    // initialise joystick
    $scope.position = {
        x: 0,
        y: 0
        };
    $scope.k9 = K9;
    $scope.changeMotorCtrl = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.motorctrl==true) {
            value="on";
          } else {
            value="off";
          };
        console.log("MotorCtrl button sent "+value);
        NRInstruction.send('navigation', "motorctrl", value);
    }
    $scope.getMPH = function (value) {
       // 0.97 is the conversion factor from 0-100 to speed of dog
       value = Math.round(value * 0.97)/10;
       value = String(value) + " mph"
       return value
       }
}])

// Controller for K9 On/Off Tab
.controller('PowerCtrl',["$scope","K9","NRInstruction", function($scope, K9, NRInstruction) {
    $scope.k9 = K9;
    $scope.changeLights = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.lights==true) {
            value="on";
          } else {
            value="off";
          };
        console.log("Lights button sent "+value);
        NRInstruction.send('toggle', "lights", value);
    }
    $scope.changeHover = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.hover==true) {
            value="on";
          } else {
            value="off";
          };
        console.log("Hover button sent "+value);
        NRInstruction.send('toggle', "hover", value);
    }
    $scope.changeEyes = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.eyes==true) {
            value="on";
          } else {
            value="off";
          };
        console.log("Eyes button sent "+value);
        NRInstruction.send('toggle', "eyes", value);
    }
    $scope.changeScreen = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.screen==true) {
            value="on";
          } else {
            value="off";
          };
        console.log("Screen button sent "+value);
        NRInstruction.send('toggle', "screen", value);
    }
}])

// Controller for K9 Servos Tab
.controller('ServoCtrl',["$scope", "NRInstruction", function($scope, NRInstruction) {
     $scope.dogstatus = {};
     $scope.changeHead = function() {
      NRInstruction.send('toggle','head',$scope.dogstatus.head);
      if ($scope.dogstatus.head == "up" ) {
        $scope.dogstatus.pwmhead="220";
        } else {
        $scope.dogstatus.pwmhead="430";
        }
      }
    $scope.changeTail = function() {
      NRInstruction.send('toggle','tail',$scope.dogstatus.tail);
      if ($scope.dogstatus.tail == "up" ) {
        $scope.dogstatus.pwmverttail="270";
        } else {
        $scope.dogstatus.pwmverttail="370";
        }
      }
    $scope.setHeadPWM = function() {
    if (parseInt($scope.dogstatus.pwmhead) <= 325) {
      $scope.dogstatus.head = "up"
      } else {
      $scope.dogstatus.head = "down"
      }
      NRInstruction.send('servo','head',$scope.dogstatus.pwmhead);
    }
    $scope.setTailVPWM = function() {
    if (parseInt($scope.dogstatus.pwmverttail) <= 320) {
      $scope.dogstatus.tail = "up"
      } else {
      $scope.dogstatus.tail = "down"
      }
        NRInstruction.send('servo','tailv',$scope.dogstatus.pwmverttail);
    }
    $scope.setTailHPWM = function() {
        NRInstruction.send('servo','tailh',$scope.dogstatus.pwmhoriztail);
    }
    $scope.setEarRPWM = function() {
        NRInstruction.send('servo','earr',$scope.dogstatus.pwmrightear);
    }
    $scope.setEarLPWM = function() {
        NRInstruction.send('servo','earl',$scope.dogstatus.pwmleftear);
    }
  }])

// Controller for K9 Audio Tab
.controller('AudioCtrl',["$scope","NRInstruction", function($scope, NRInstruction) {
    // receive button click event and send mood message
    $scope.buttonClick = function(event) {
      NRInstruction.send('mood', event.target.id,'null');
      }
  }])

// Controller for K9 Sensor Tab
.controller('SensorsCtrl',["$scope","msgtoPoint", function($scope,msgtoPoint) {
    // Load SVG picture of K9
    var s = Snap("#k9sensors")
    var mySensorArray=[];
    var bigline;
    Snap.load("img/K9 sensors.svg", onSVGLoaded );
    // view needs to be kept in line with the sensorArray object
    // ideally back1 to back6 will have a line joining them
    // perhaps a setInterval refresh of
    function onSVGLoaded( data ){
      s.append( data );
      var plot;
      var x_pos;
      var y_pos;
      var sensor_name;
      // Centrepoint {"sensorName":"centre","x": 320,"y":568},
      var readingsData = '[{"sensorName":"ultrasonic","x": 1200,"y":1200,"angle":999},{"sensorName":"l_ear","x": 1158,"y":890,"angle":999},{"sensorName":"r_ear","x": 1242,"y":890,"angle":999},{"sensorName":"left","x": 1120,"y":1343,"angle":180},{"sensorName":"bl_corner","x": 1152,"y":1411,"angle":225},{"sensorName":"tail","x": 1200,"y":1430,"angle":270},{"sensorName":"br_corner","x": 1248,"y":1411,"angle":315},{"sensorName":"right","x": 1280,"y":1343,"angle":0}]';
      var readings = JSON.parse(readingsData);
      // indexed iteration
      for (var key in readings) {
        if (!readings.hasOwnProperty(key)) {
        //The current property is not a direct property of p
        continue;
        }
        //Do your logic with the property here
        x_pos = readings[key].x;
        y_pos = readings[key].y;
        sensor_name = readings[key].sensorName;
        plot = s.circle(x_pos,y_pos,10);
        plot.attr({fill: "#00ff00",});
        // console.log(sensor_name + ": x-"+ x_pos + " y-" + y_pos);
      }
      mySensorArray=msgtoPoint.getSensorArray();
      $scope.ultrasonic = s.line(1200,1200,parseInt(mySensorArray[0].x),parseInt(mySensorArray[0].y));
      $scope.ultrasonic.attr({
        stroke: "#ff0000",
        strokeWidth: 10
        });
      $scope.line1 = s.line(parseInt(mySensorArray[2].x),parseInt(mySensorArray[2].y),parseInt(mySensorArray[3].x),parseInt(mySensorArray[3].y));
      $scope.line2 = s.line(parseInt(mySensorArray[3].x),parseInt(mySensorArray[3].y),parseInt(mySensorArray[4].x),parseInt(mySensorArray[4].y));
      $scope.line3 = s.line(parseInt(mySensorArray[4].x),parseInt(mySensorArray[4].y),parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y));
      $scope.line3 = s.line(parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y),parseInt(mySensorArray[6].x),parseInt(mySensorArray[6].y));
      $scope.bigline = s.group($scope.line1, $scope.line2, $scope.line3);
      $scope.bigline.attr({
        stroke: "#00ff00",
        strokeWidth: 10
        });
      $scope.rdtime=setInterval(function() {$scope.reDraw();},200);
    }
    $scope.reDraw = function () {
      // method to reDraw sensor screen
      mySensorArray=msgtoPoint.getSensorArray();
      $scope.ultrasonic.animate({ x1: 1200, x2: mySensorArray[0].x, y1: 1200, y2: mySensorArray[0].y},100);
      $scope.line1.animate({ x1: mySensorArray[2].x, x2: mySensorArray[2].x, y1: mySensorArray[3].y, y2: mySensorArray[3].y},100);
      $scope.line2.animate({ x1: mySensorArray[3].x, x2: mySensorArray[3].x, y1: mySensorArray[4].y, y2: mySensorArray[4].y},100);
      $scope.line3.animate({ x1: mySensorArray[4].x, x2: mySensorArray[4].x, y1: mySensorArray[5].y, y2: mySensorArray[5].y},100);
      $scope.line3.animate({ x1: mySensorArray[5].x, x2: mySensorArray[5].x, y1: mySensorArray[6].y, y2: mySensorArray[6].y},100);
      //console.log("Sensor array: " + JSON.stringify(mySensorArray));
      }
  }])

// Controller for K9 Settings Tab
.controller('SettingsCtrl', function($scope, NodeREDConnection) {
  // retrieve stored node-Red socket settings
  $scope.K9settings = NodeREDConnection.getSettings();
  // include slash or not
  $scope.getFiller = function(directory) {
  if (directory=="") {return "";} else {return "/";}
  }
  // save and connect to node-Red via socket
  $scope.connect = function () {
    NodeREDConnection.saveSettings($scope.K9settings);
    NodeREDConnection.connect($scope.K9settings);
    $scope.connected = 'button button-balanced icon-left ion-locked';
    }
  $scope.disconnect = function () {
    if ($scope.connected == "button button-assertive icon-left ion-unlocked")
    {
      $scope.connect($scope.K9settings);
    } else {
      NodeREDConnection.disconnect();
      $scope.connected = 'button button-assertive icon-left ion-unlocked';
    }
    }

});
