// 'use strict';

angular.module('K9.directives', [])

// myDirectives.directive('nrStatusIcon',['NodeREDSocket', function(NodeREDSocket) {
.directive('nrStatusIcon',['NodeREDConnection', function(NodeREDConnection) {
  return {
    restrict: 'E',
    replace: 'true',
    template: '<button class={{icon}}></button>',
    link: function (scope, element, attrs) {
        scope.$watch(
        function(){return NodeREDConnection.status()},
        function(newVal,oldVal) {
          scope.icon = newVal;
          // console.log("Indirective: " + newVal);}
        })
      }
    }
}])

.directive('joystick',['NRInstruction','K9', function(NRInstruction,K9) {

    function joystickController ($scope) {
    }
    return {
        restrict : 'E',
        controller : ['$scope', function ($scope) {
            return joystickController($scope);
        }],
        scope : {
            // this binds position to the position attribute of the directive
            // the equals on its own denotes the same name
            position : '='
        },
        template : '<svg id="k9joystick" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200px" height="200px"></svg>',
        link : function(scope, element, attrs) {
           console.log("I got here!")
            // bring the K9 object into directive scope
            //scope.k9 = K9;
            // declare rest position for joystick
            CENTRE_X = 100
            CENTRE_Y = 100
            // put jostick position at rest
            joy_position = {
                x : CENTRE_X,
                y : CENTRE_Y
            }
            // initialise position as 0
            scope.position = {
              x : 0,
              y : 0
            }
            // send a value between -100 and +100 on the x and y axis to
            // the node-RED controller
            function send(joy_position){
               console.log("Sending position")
               scope.position.x = joy_position.x;
               scope.position.y = joy_position.y;
               NRInstruction.send('navigation', scope.position.x, scope.position.y);
            }
            // create a Snap paper in HTML element joystick
            var s = Snap("#k9joystick");
            var turbo = false;
            var msg_turbo = "off"
            var joystick_pic = Snap.load("img/Joystick Slow.svg", onJoyLoaded);
            // draw the joystick circle
            var joy = s.circle(joy_position.x,joy_position.y,10);
            // initialise as green or red depending upon turbo value
            joy.attr({
              stroke: "none",  // NEED TO LINK TO TOGGLEVALUE
              strokeWidth: 10,
              fill : "green"
            });
            s.append(joy)
/*
            scope.$watch('k9.motorctrl', function() {
              console.log("Status change"+k9.motorctrl);
              if (k9.motorctrl==true) {
                joy.attr({
                  fill : "green",
                  cr : 20,
                });
                // also change which joystick shown
              }
              else {
                joy.attr({
                  fill : "red",
                  cr : 40,
                });
                // also change which joystick shown
                // delete old joystick
              }
              });
             */
            // Update joystick view
            function onJoyLoaded(data){
               s.clear();
               s.append(data);
               s.append(joy);
                }

            var move = function(dx, dy, x, y){
              console.log("Moving!");
              var clientX, clientY;
              if ((typeof dx=='object')&&(dx.type=='touchmove')) {
                 clientX = dx.changedTouches[0].clientX;
                 clientY = dx.changedTouches[0].clientY;
                 dx = clientX - this.data('ox');
                 dy = clientY - this.data('oy');
              }
              if (turbo === false){
                 if (Math.abs(dx)>Math.abs(dy)){
                    dy=0;
                 }
                 else {
                    dx=0;
                 }
              }
              this.attr({
                 transform: this.data('origTransform') + (this.data('origTransform') ? "T":"t") + [dx,dy]
              });
              joy_position.x = dx;
              joy_position.y = dy*-1;
              //this.attr({
               //     cx: joy_position.x,
               //     cy: joy_position.y
               // });
               //console.log("x: "+x+", dx:"+dx+", y: "+y+", dx:"+dy);
              send(joy_position);
            }

            var start = function(x,y,ev) {
               if((typeof x=='object')&&(x.type=="touchstart")){
                  x.preventDefault();
                  this.data('ox',x.changedTouches[0].clientX);
                  this.data('oy',x.changedTouches[0].clientY);
               }
               this.data('origTransform',this.transform().local);
               console.log("Joystick touch detected");
            }

            var stop = function() {
              console.log('Let go of joystick');
              // need to reset joystick to zero and make joystick transparent
              joy_position.x = 0;
              joy_position.y = 0;
              dx = 0;
              dy = 0;
              this.attr({
                 transform: this.data('origTransform') + (this.data('origTransform') ? "T":"t") + [dx,dy]
            });
              send(joy_position);
            }

            var doubleclick = function(){
               if (turbo === false){
                  turbo = true;
                  msg_turbo="on";
                  joystick_pic = Snap.load("img/Joystick Turbo.svg", onJoyLoaded);
                  joy.attr({
                    fill : "red",
                    r : 30,
                  });
                  s.append(joy);
                  console.log("TURBO mode");
               }
               else {
                  turbo = false;
                  msg_turbo="off";
                  joystick_pic = Snap.load("img/Joystick Slow.svg", onJoyLoaded);
                  joy.attr({
                    fill : "green",
                    r : 10,
                  });
                  s.append(joy);
                  console.log("slow mode");
               }
               console.log('Double click');
               NRInstruction.send('navigation', "motorctrl", msg_turbo);
            }

            // register the functions above against the Snap SVG drag movement
            console.log("Registering joystick functions")
            joy.drag(move,start,stop);
            joy.dblclick(doubleclick);
            s.append(joy);
    }
  };
}])
