angular.module('K9.controllers', [])

// Controller for K9 Motor Tab
.controller('MotorCtrl', function($scope, NRInstruction) {
    // initialise joystick
      $scope.position ={
        x: 0,
        y: 0
        };
  })

// Controller for K9 On/Off Tab
.controller('PowerCtrl', function($scope, NRInstruction) {
    $scope.settingsList = [
    { text: "Eyes Lights", checked: false, id: "eyes" },
    { text: "Back Lights", checked: false, id: "lights" },
    { text: "Hover Lights", checked: false, id: "hover" },
    { text: "Display Screen", checked: false, id: "screen" }
    ];
    $scope.changeCheckItem = function (item) {
    var value;
    if (item.checked) {value="on"} else {value="off"};
    NRInstruction.send('toggle', item.id, value);
    }
  })

// Controller for K9 Servos Tab
.controller('ServoCtrl', function($scope, NRInstruction) {
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
  })

// Controller for K9 Audio Tab
.controller('AudioCtrl', function($scope, NRInstruction) {
    // receive button click event and send mood message
    $scope.buttonClick = function(event) {
      NRInstruction.send('mood', event.target.id,'null');
      }
  })

// Controller for K9 Sensor Tab
.controller('SensorsCtrl', function($scope) {
    /* Temporary chart data */
    var s = Snap("#k9sensors");
    Snap.load("img/K9 m2-01.svg", onSVGLoaded );
    function onSVGLoaded( data ){
      s.append( data );
      var plot;
      var x_pos;
      var y_pos;
      var sensor_name;
      var readingsData = '[{"sensorName":"centre","x": 320,"y":568},{"sensorName":"leftear","x": 306,"y":452},{"sensorName":"rightear","x": 335,"y":452},{"sensorName":"front","x": 320,"y":463},{"sensorName":"back1","x": 291,"y":593},{"sensorName":"back6","x": 350,"y":593},{"sensorName":"back2","x": 298,"y":612},{"sensorName":"back5","x": 346,"y":612},{"sensorName":"back3","x": 310,"y":620},{"sensorName":"back4","x": 333,"y":620},{"sensorName":"back","x": 320,"y":740}]';
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
        console.log(sensor_name + ": x-"+ x_pos + " y-" + y_pos);
      }
    }
    })
    // Lets create big circle in the middle:
    // var bigCircle = s.circle(150, 150, 5);
    // By default its black, lets change its attributes
   //bigCircle.attr({
   // fill: "#33CD5F",
   //});
   // }
   // var data = '[{"cohortName": "Boston Public Schools","value": 0.3337727272727273},{"cohortName": "Stanley Middle School","value": 0.2844818181818182},{"cohortName": "My Students","value": 0.1590909090909091}]';
   // what does the sensor have to react to?


// Controller for K9 Settings Tab
.controller('SettingsCtrl', function($scope, NodeREDConnection) {
  // retrieve stored node-Red socket settings
  $scope.K9settings = NodeREDConnection.getSettings();
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
