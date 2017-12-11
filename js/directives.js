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
          // console.log("Indirective: " + newVal);
          }
        )}
      }
}])

.directive('joystick',['NRInstruction','K9' function(NRInstruction,K9) {

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
        template : '<svg id="joystick" version="1.1" xmlns="http://www.w3.org/2000/svg" height="200" width="200"></svg>',
        link : function(scope, element) {
            // bring the K9 object into directive scope
            $scope.k9 = K9;
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
              scope.position.x = joy_position.x - CENTRE_X;
              scope.position.y = joy_position.y - CENTRE_Y;
              NRInstruction.send('navigation', scope.position.x, scope.position.y);
            }
            // create a Snap paper in HTML element joystick
            var s = Snap("#joystick");
            // draw the joystick circle
            var joystick = s.circle(joy_position.x,joy_position.y,20);
            // initialise as green or red depending upon turbo value
            joystick.attr({
              stroke: "none",  // NEED TO LINK TO TOGGLEVALUE
              strokeWidth: 10,
              fill = "none"
            });

            // Link the status of the Turbo button to then
            // joystick picture being shown and the joystick
            // appearance itself
            scope.$watch('k9.motorctrl', function() {
              if k9.motorctrl==true {
                joystick.attr({
                  fill = "green",
                  cr = 20,
                });
                // also change which joystick shown
              }
              else {
                joystick.attr({
                  fill = "red",
                  cr = 40,
                });
                // also change which joystick shown
                // delete old joystick
              }
              });


                          var joystick = Snap.load("img/Joystick Turbo.svg", onJoyLoaded);
                          // Update joystick view
                          function onJoyLoaded(data){
                            j.append(data);
                          }



            var move = function(dx, dy){
              console.log("Moving!");
              joy_position.x = joy_position.x + dx;
              joy_position.y = joy_position.y + dy
                  };
              this.attr({
                    cx: joy_position.x,
                    cy: joy_position.y
                });
              send(joy_position);
            }

            var start = function() {
              console.log("Joystick touch detected");
            }

            var stop = function() {
              console.log('Let go of joystick');
              // need to reset joystick to zero and make joystick transparent
              joy_position.x = CENTRE_X;
              joy_position.y = CENTRE_Y;
              send(joy_position);
            }
            // register the functions above against the Snap SVG drag movement
            joystick.drag(move,start,stop);
        }

    };

}])
