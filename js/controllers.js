angular.module('K9.controllers', [])

// Controller for K9 Follow Me Tab
.controller('FollowCtrl',["$scope","K9","NRInstruction","msgtoPoint","NodeREDConnection", function($scope, K9, NRInstruction, msgtoPoint, NodeREDConnection) {
    // SVG
    var j = Snap("#k9joystick");
    var s = Snap("#k9sensors");
    Snap.load("img/K9 sensors.svg", onSVGLoaded);
    //Snap.load("img/Joystick Slow.svg", onJoyLoaded);
    // Update joystick view
    function onJoyLoaded( data ){
      j.append( data );
    }
    // Update sensor view
    function onSVGLoaded( data ){
      s.append( data );
      var plot;
      var x_pos;
      var y_pos;
      var sensor_name;
      //var readingsData = '[{"sensorName":"ultrasonic","x": 1200,"y":1200,"angle":999},{"sensorName":"l_ear","x": 1158,"y":890,"angle":999},{"sensorName":"r_ear","x": 1242,"y":890,"angle":999},{"sensorName":"left","x": 1120,"y":1343,"angle":180},{"sensorName":"bl_corner","x": 1152,"y":1411,"angle":225},{"sensorName":"tail","x": 1200,"y":1430,"angle":270},{"sensorName":"br_corner","x": 1248,"y":1411,"angle":315},{"sensorName":"right","x": 1280,"y":1343,"angle":0}]';
      //var readings = JSON.parse(readingsData);
      // indexed iteration
      /*
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
      */
      mySensorArray=msgtoPoint.getSensorArray();
      //$scope.ultrasonic = s.line(1200,1200,parseInt(mySensorArray[0].x),parseInt(mySensorArray[0].y));
      $scope.ultrasonic = s.circle(parseInt(mySensorArray[0].x),parseInt(mySensorArray[0].y),75).attr({fill:'#33cd5f',strokeWidth:35,stroke:'#7a7a7a'});
      $scope.line1 = s.line(parseInt(mySensorArray[1].x),parseInt(mySensorArray[1].y),parseInt(mySensorArray[2].x),parseInt(mySensorArray[2].y));
      $scope.line2 = s.line(parseInt(mySensorArray[2].x),parseInt(mySensorArray[2].y),parseInt(mySensorArray[3].x),parseInt(mySensorArray[3].y));
      $scope.line3 = s.line(parseInt(mySensorArray[3].x),parseInt(mySensorArray[3].y),parseInt(mySensorArray[4].x),parseInt(mySensorArray[4].y));
      $scope.line4 = s.line(parseInt(mySensorArray[4].x),parseInt(mySensorArray[4].y),parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y));
      $scope.line5 = s.line(parseInt(mySensorArray[5].x),parseInt(mySensorArray[5].y),parseInt(mySensorArray[6].x),parseInt(mySensorArray[6].y));
      $scope.line6 = s.line(parseInt(mySensorArray[6].x),parseInt(mySensorArray[6].y),parseInt(mySensorArray[7].x),parseInt(mySensorArray[7].y));
      $scope.line7 = s.line(parseInt(mySensorArray[7].x),parseInt(mySensorArray[7].y),parseInt(mySensorArray[8].x),parseInt(mySensorArray[8].y));
      $scope.line8 = s.line(parseInt(mySensorArray[8].x),parseInt(mySensorArray[8].y),parseInt(mySensorArray[9].x),parseInt(mySensorArray[9].y));
      $scope.line9 = s.line(parseInt(mySensorArray[9].x),parseInt(mySensorArray[9].y),parseInt(mySensorArray[10].x),parseInt(mySensorArray[10].y));
      $scope.line10 = s.line(parseInt(mySensorArray[10].x),parseInt(mySensorArray[10].y),parseInt(mySensorArray[11].x),parseInt(mySensorArray[11].y));
      $scope.line11 = s.line(parseInt(mySensorArray[11].x),parseInt(mySensorArray[11].y),parseInt(mySensorArray[12].x),parseInt(mySensorArray[12].y));
      $scope.line12 = s.line(parseInt(mySensorArray[12].x),parseInt(mySensorArray[12].y),parseInt(mySensorArray[13].x),parseInt(mySensorArray[13].y));
      $scope.line13 = s.line(parseInt(mySensorArray[13].x),parseInt(mySensorArray[13].y),parseInt(mySensorArray[14].x),parseInt(mySensorArray[14].y));
      $scope.line14 = s.line(parseInt(mySensorArray[14].x),parseInt(mySensorArray[14].y),parseInt(mySensorArray[15].x),parseInt(mySensorArray[15].y));
      $scope.line15 = s.line(parseInt(mySensorArray[15].x),parseInt(mySensorArray[15].y),parseInt(mySensorArray[16].x),parseInt(mySensorArray[16].y));
      $scope.line16 = s.line(parseInt(mySensorArray[16].x),parseInt(mySensorArray[16].y),parseInt(mySensorArray[17].x),parseInt(mySensorArray[17].y));
      $scope.line17 = s.line(parseInt(mySensorArray[17].x),parseInt(mySensorArray[17].y),parseInt(mySensorArray[18].x),parseInt(mySensorArray[18].y));

      $scope.line18 = s.line(parseInt(mySensorArray[19].x),parseInt(mySensorArray[19].y),parseInt(mySensorArray[20].x),parseInt(mySensorArray[20].y));
      $scope.line19 = s.line(parseInt(mySensorArray[20].x),parseInt(mySensorArray[20].y),parseInt(mySensorArray[21].x),parseInt(mySensorArray[21].y));
      $scope.line20 = s.line(parseInt(mySensorArray[21].x),parseInt(mySensorArray[21].y),parseInt(mySensorArray[22].x),parseInt(mySensorArray[22].y));
      $scope.line21 = s.line(parseInt(mySensorArray[22].x),parseInt(mySensorArray[22].y),parseInt(mySensorArray[23].x),parseInt(mySensorArray[23].y));
      $scope.bigline = s.group($scope.line1, $scope.line2, $scope.line3, $scope.line4, $scope.line5, $scope.line6, $scope.line7, $scope.line8, $scope.line9, $scope.line10, $scope.line11, $scope.line12, $scope.line13, $scope.line14, $scope.line15, $scope.line16, $scope.line17, $scope.line18, $scope.line19, $scope.line20, $scope.line21);
      $scope.bigline.attr({
        stroke: "#7a7a7a",
        strokeWidth: 35,
        strokeLinecap: "round"
        });

      $scope.rdtime=setInterval(function() {$scope.reDraw();},60);
    }
    $scope.reDraw = function () {
      // method to reDraw sensor screen
      mySensorArray=msgtoPoint.getSensorArray();
      $scope.ultrasonic.animate({cx: mySensorArray[0].x,cy: mySensorArray[0].y},60,mina.easein);

      $scope.line1.animate({ x1: mySensorArray[1].x, x2: mySensorArray[2].x, y1: mySensorArray[1].y, y2: mySensorArray[2].y},30);
      $scope.line2.animate({ x1: mySensorArray[2].x, x2: mySensorArray[3].x, y1: mySensorArray[2].y, y2: mySensorArray[3].y},30);
      $scope.line3.animate({ x1: mySensorArray[3].x, x2: mySensorArray[4].x, y1: mySensorArray[3].y, y2: mySensorArray[4].y},30);
      $scope.line4.animate({ x1: mySensorArray[4].x, x2: mySensorArray[5].x, y1: mySensorArray[4].y, y2: mySensorArray[5].y},30);
      $scope.line5.animate({ x1: mySensorArray[5].x, x2: mySensorArray[6].x, y1: mySensorArray[5].y, y2: mySensorArray[6].y},30);
      $scope.line6.animate({ x1: mySensorArray[6].x, x2: mySensorArray[7].x, y1: mySensorArray[6].y, y2: mySensorArray[7].y},30);
      $scope.line7.animate({ x1: mySensorArray[7].x, x2: mySensorArray[8].x, y1: mySensorArray[7].y, y2: mySensorArray[8].y},30);
      $scope.line8.animate({ x1: mySensorArray[8].x, x2: mySensorArray[9].x, y1: mySensorArray[8].y, y2: mySensorArray[9].y},30);
      $scope.line9.animate({ x1: mySensorArray[9].x, x2: mySensorArray[10].x, y1: mySensorArray[9].y, y2: mySensorArray[10].y},30);
      $scope.line10.animate({ x1: mySensorArray[10].x, x2: mySensorArray[11].x, y1: mySensorArray[10].y, y2: mySensorArray[11].y},30);
      $scope.line11.animate({ x1: mySensorArray[11].x, x2: mySensorArray[12].x, y1: mySensorArray[11].y, y2: mySensorArray[12].y},30);
      $scope.line12.animate({ x1: mySensorArray[12].x, x2: mySensorArray[13].x, y1: mySensorArray[12].y, y2: mySensorArray[13].y},30);
      $scope.line13.animate({ x1: mySensorArray[13].x, x2: mySensorArray[14].x, y1: mySensorArray[13].y, y2: mySensorArray[14].y},30);
      $scope.line14.animate({ x1: mySensorArray[14].x, x2: mySensorArray[15].x, y1: mySensorArray[14].y, y2: mySensorArray[15].y},30);
      $scope.line15.animate({ x1: mySensorArray[15].x, x2: mySensorArray[16].x, y1: mySensorArray[15].y, y2: mySensorArray[16].y},30);
      $scope.line16.animate({ x1: mySensorArray[16].x, x2: mySensorArray[17].x, y1: mySensorArray[16].y, y2: mySensorArray[17].y},30);
      $scope.line17.animate({ x1: mySensorArray[17].x, x2: mySensorArray[18].x, y1: mySensorArray[17].y, y2: mySensorArray[18].y},30);

      $scope.line18.animate({ x1: mySensorArray[19].x, x2: mySensorArray[20].x, y1: mySensorArray[19].y, y2: mySensorArray[20].y},30);
      $scope.line19.animate({ x1: mySensorArray[20].x, x2: mySensorArray[21].x, y1: mySensorArray[20].y, y2: mySensorArray[21].y},30);
      $scope.line20.animate({ x1: mySensorArray[21].x, x2: mySensorArray[22].x, y1: mySensorArray[21].y, y2: mySensorArray[22].y},30);
      $scope.line21.animate({ x1: mySensorArray[22].x, x2: mySensorArray[23].x, y1: mySensorArray[22].y, y2: mySensorArray[23].y},30);

      //console.log("Sensor array: " + JSON.stringify(mySensorArray));
      }
    // initialise joystick
    $scope.position = {
        x: 0,
        y: 0
        };
    $scope.k9 = K9;

/*
    $scope.changeMotorCtrl = function (status) {
        // console.log(status);
        var value;
        if ($scope.k9.motorctrl==true) {
            value="on";
          }
          else
          {
            value="off";
          };
        // console.log("MotorCtrl button sent "+value);
        NRInstruction.send('navigation', "motorctrl", value);
    }
    */

    // sends mood from button clicks
    $scope.buttonClick = function(event) {
      NRInstruction.send('mood', event.target.id,'null');
      }

    $scope.connectToK9 = function(){
      $scope.K9settings = NodeREDConnection.getSettings();
      NodeREDConnection.connect($scope.K9settings);
      $scope.connected = 'button button-balanced icon-left ion-locked';
    }

  // listens for and event from the Node Red Instruction service that
  // indicates that a k9 status message has been received from the
  // Python Controller websocket.  As a result, this function updates the
  // k9 object held in $scope, enabling the gauges to be updated
  $scope.$on("event:k9state", function(evt,data){
         $scope.k9.setStatus(data);
       });
}])

// Controller for K9 On/Off Tab
.controller('PowerCtrl',["$scope","K9","NRInstruction", function($scope, K9, NRInstruction) {
     $scope.k9 = K9;
     $scope.dogstatus = {};

     $scope.changeLights = function (status) {
         // console.log(status);
         var value;
         if ($scope.k9.lights==true) {
             value="on";
           } else {
             value="off";
           };
         // console.log("Lights button sent "+value);
         NRInstruction.send('toggle', "lights", value);
     }

     $scope.changeScreen = function (status) {
         // console.log(status);
         var value;
         if ($scope.k9.screen==true) {
             value="on";
           } else {
             value="off";
           };
         // console.log("Screen button sent "+value);
         NRInstruction.send('toggle', "screen", value);
     }

      $scope.changeEyes = function() {
        NRInstruction.send('toggle','eyes',$scope.dogstatus.eyes);
        if ($scope.dogstatus.eyes == "on" ) {
          $scope.dogstatus.pwmeyes="100";
          } else {
          $scope.dogstatus.pwmeyes="0";
          }
        }
     $scope.setEyesPWM = function() {
     if (parseInt($scope.dogstatus.pwmeyes) <= 50) {
       $scope.dogstatus.eyes = "off"
       } else {
       $scope.dogstatus.eyes = "on"
       }
       NRInstruction.send('servo','eyes',$scope.dogstatus.pwmeyes);
     }


 $scope.changeHover = function() {
   NRInstruction.send('toggle','hover',$scope.dogstatus.hover);
   if ($scope.dogstatus.hover == "on" ) {
     $scope.dogstatus.pwmhover="100";
     } else {
     $scope.dogstatus.pwmhover="0";
     }
   }
$scope.setHoverPWM = function() {
if (parseInt($scope.dogstatus.pwmhover) <= 50) {
  $scope.dogstatus.hover = "off"
  } else {
  $scope.dogstatus.hover = "on"
  }
  NRInstruction.send('servo','hover',$scope.dogstatus.pwmhover);
}

$scope.changeTail = function() {
  NRInstruction.send('toggle','tail',$scope.dogstatus.tail);
  if ($scope.dogstatus.tail == "down" ) {
    $scope.dogstatus.pwmverttail="370";
    } else {
    $scope.dogstatus.pwmverttail="270";
    }
  }

 $scope.setTailVPWM = function() {
 if (parseInt($scope.dogstatus.pwmverttail) <= 320) {
   $scope.dogstatus.tail = "up"
   } else {
   $scope.dogstatus.tail = "down"
   }
     NRInstruction.send('servo','tailv',$scope.dogstatus.pwmverttail);
 }

 $scope.changeTailH = function() {
   NRInstruction.send('toggle','tailh',$scope.dogstatus.tailh);
   if ($scope.dogstatus.tailh == "right" ) {
     $scope.dogstatus.pwmhoriztail="440";
     } else {
     $scope.dogstatus.pwmhoriztail="325";
     }
   }

  $scope.setTailHPWM = function() {
  if (parseInt($scope.dogstatus.pwmhoriztail) <= 380) {
    $scope.dogstatus.tailh = "left"
    } else {
    $scope.dogstatus.tailh = "right"
    }
      NRInstruction.send('servo','tailh',$scope.dogstatus.pwmhoriztail);
  }

  }])

// Controller for K9 Audio Tab
.controller('AudioCtrl',["$scope","NRInstruction", function($scope, NRInstruction) {
    // receive button click event and send mood message
    $scope.buttonClick = function(event) {
      NRInstruction.send('mood', event.target.id,'null');
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
