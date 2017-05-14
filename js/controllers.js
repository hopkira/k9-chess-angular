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
    Snap.load("img/K9 m2-01.svg", onSVGLoaded );
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
      var readingsData = '[{"sensorName":"leftear","x": 306,"y":452},{"sensorName":"rightear","x": 335,"y":452},{"sensorName":"front","x": 320,"y":463},{"sensorName":"back1","x": 291,"y":593},{"sensorName":"back6","x": 350,"y":593},{"sensorName":"back2","x": 298,"y":612},{"sensorName":"back5","x": 346,"y":612},{"sensorName":"back3","x": 310,"y":620},{"sensorName":"back4","x": 333,"y":620},{"sensorName":"back","x": 320,"y":740}]';
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
        plot = s.circle(x_pos,y_pos,5);
        plot.attr({fill: "#33CD5F",});
        // console.log(sensor_name + ": x-"+ x_pos + " y-" + y_pos);
      }
      mySensorArray=msgtoPoint.getSensorArray();
      $scope.line1 = s.line(parseInt(mySensorArray[3].x),parseInt(mySensorArray[3].y),parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y));
      $scope.line2 = s.line(parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y),parseInt(mySensorArray[7].x),parseInt(mySensorArray[7].y));
      $scope.line3 = s.line(parseInt(mySensorArray[7].x),parseInt(mySensorArray[7].y),parseInt(mySensorArray[8].x),parseInt(mySensorArray[8].y));
      $scope.bigline = s.group($scope.line1, $scope.line2, $scope.line3);
      $scope.bigline.attr({
        stroke: "#33CD5F",
        strokeWidth: 5
        });
      $scope.rdtime=setInterval(function() {$scope.reDraw();},200);
    }
    $scope.reDraw = function () {
      // method to reDraw sensor screen
      mySensorArray=msgtoPoint.getSensorArray();
      $scope.line1.animate({ x1: mySensorArray[3].x, x2: mySensorArray[5].x, y1: mySensorArray[3].y, y2: mySensorArray[5].y},100);
      $scope.line2.animate({ x1: mySensorArray[5].x, x2: mySensorArray[7].x, y1: mySensorArray[5].y, y2: mySensorArray[7].y},100);
      $scope.line3.animate({ x1: mySensorArray[7].x, x2: mySensorArray[8].x, y1: mySensorArray[7].y, y2: mySensorArray[8].y},100);
      // console.log("Sensor array: " + JSON.stringify(mySensorArray));
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
