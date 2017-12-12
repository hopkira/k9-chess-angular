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
        )}
      }
}])

.directive('joystick',['NRInstruction', function(NRInstruction) {

    function joystickController ($scope) {
    }
    return {
        restrict : 'E',
        controller : ['$scope', function ($scope) {
            return joystickController($scope);
        }],
        scope : {
            position : '='
        },
        template : '<canvas class="joystickCanvas"></canvas>',
        link : function(scope, element) {

            // these variables define the two centre circles
            var joystickHeight = 200;
            var joystickWidth  = 200;

            var centre = {
                x : joystickHeight / 2,
                y : joystickWidth / 2
            };

            var radiusCircle = 35;
            var radiusBound = 50;

            // Canvas and context element
            var container = element[0];
            var canvas = container.children[0];
            var ctx = canvas.getContext('2d');

            // Id of the touch on the cursor
            var cursorTouchId = -1;
            // cursor touch object is initialised as half size of joystick
            var cursorStart = {
                x : centre.x,
                y : centre.y
            };
            var cursorDelta = {
                x : 0,
                y : 0
            };

            // canvas is the same size as the joystick
            function resetCanvas() {
                canvas.height = joystickHeight;
                canvas.width = joystickWidth;
            }

            // customerTouch object is the touch point
            function onTouchStart(event) {
                var touch = event.targetTouches[0];
                cursorTouchId = touch.identifier;
            // identify where the cursor has touched and store in cursorStart object
                cursorStart = {
                    x : touch.pageX - touch.target.offsetLeft,
                    y : touch.pageY - touch.target.offsetTop
                };
            }

            function onTouchMove(event) {
                // Prevent the browser from doing its default thing (scroll, zoom)
                event.preventDefault();
                for(var i = 0; i < event.changedTouches.length; i++){
                    var touch = event.changedTouches[i];

                    if(cursorTouchId === touch.identifier)
                    {
                        // calculate where the joystick now is
                        cursorNow = {
                            x : touch.pageX - touch.target.offsetLeft,
                            y : touch.pageY - touch.target.offsetTop
                        };
                        cursorDelta = {
                          x : cursorNow.x - cursorStart.x,
                          y : cursorNow.y - cursorStart.y
                          };
                        cursorNormalised = {
                          x : Math.round(cursorDelta.x/joystickWidth*200),
                          y : Math.round(cursorDelta.y/joystickHeight*-200)
                          };


                        scope.$apply(
                            scope.position = {
                                x : cursorNormalised.x,
                                y : cursorNormalised.y
                            }
                        );

                        break;
                    }
                }

            }

            function onTouchEnd() {

                cursorTouchId = -1;

                scope.$apply(
                    scope.position = {
                        x : 0,
                        y : 0
                    }
                );
                cursorStart.x = centre.x;
                cursorStart.y = centre.y;
                cursorDelta.x = 0;
                cursorDelta.y = 0;
                cursorNow.x = centre.x;
                cursorNow.y = centre.y;
            }

            function draw() {
                // Clear the canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.beginPath();
                ctx.strokeStyle = '#00ce5c';
                ctx.lineWidth = 10;
                ctx.arc(centre.x + cursorDelta.x, centre.y + cursorDelta.y, radiusCircle, 0, Math.PI*2, true);
                ctx.stroke();

                requestAnimFrame(draw);
            }

            // Check if touch is enabled
            var touchable = true;

            if(touchable) {
                canvas.addEventListener( 'touchstart', onTouchStart, false );
                canvas.addEventListener( 'touchmove', onTouchMove, false );
                canvas.addEventListener( 'touchend', onTouchEnd, false );

                window.onorientationchange = resetCanvas;
                window.onresize = resetCanvas;
            }
            // Bind to the values from outside as well
            scope.$watch('position', function(newval) {
                NRInstruction.send('navigation', newval.x, newval.y);
                cursorDelta = {
                    x : newval.x,
                    y : newval.y*-1
                };
            });
            resetCanvas();
            draw();

        }

    };

}])
