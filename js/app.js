// Ionic Starter App

/* Stage 1 - remote K9 control */

/* Main k9 functions follow */

/* Next lines added as minimum camera preview */
/* Server side function provided by RPi-Cam-Web */

var mjpeg_img;

function reload_img() {
    mjpeg_img.src = "cam_pic.php?time=" + new Date().getTime();
}
function error_img() {
  setTimeout("mjpeg_img.src = 'cam_pic.php?time=' + new Date().getTime();", 100);
}
function init() {
  mjpeg_img = document.getElementById("mjpeg_dest");
  mjpeg_img.onload = reload_img;
  mjpeg_img.onerror = error_img;
  reload_img();
}

window.requestAnimFrame = (function ( ){
        return  window.requestAnimationFrame   ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame    ||
            function(callback){
                window.setTimeout(callback, 1000 / 60);
        };
})();

// function distance(evt){
//	var gap = JSON.parse(evt.data);
//	gap = parseInt(gap.payload,[10]);
//	if (gap > 50) {
//      gap = 50;
//		}
//	var red = 255-(gap*5);
//	var green = 5*gap;
//	gap = rgb(red,green,0);
//	$('#forward_sensor').css('background-color',gap);
//	}

// function rgb(r, g, b){
//  return "rgb("+r+","+g+","+b+")";
// }

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
// 'starter.services' is found in services.js
// 'starter.controllers' is found in controllers.js

angular.module('K9', ['ionic','ngJustGage', 'K9.controllers', 'K9.services', 'K9.directives'])

.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if (window.cordova && window.cordova.plugins && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
      cordova.plugins.Keyboard.disableScroll(true);

    }
    if (window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
})

.config(function($stateProvider, $urlRouterProvider) {

  // Ionic uses AngularUI Router which uses the concept of states
  // Learn more here: https://github.com/angular-ui/ui-router
  // Set up the various states which the app can be in.
  // Each state's controller can be found in controllers.js
  $stateProvider

  // setup an abstract state for the tabs directive
    .state('tab', {
    url: '/tab',
    abstract: true,
    templateUrl: 'templates/tabs.html'
  })

  // Each tab has its own nav history stack:

  .state('tab.power', {
    url: '/power',
    views: {
      'tab-power': {
        templateUrl: 'templates/tab-power.html',
        controller: 'PowerCtrl'
      }
    }
  })

    .state('tab.audio', {
    url: '/audio',
    views: {
      'tab-audio': {
        templateUrl: 'templates/tab-audio.html',
        controller: 'AudioCtrl'
      }
    }
  })

  .state('tab.servo', {
      url: '/servo',
      views: {
        'tab-servo': {
          templateUrl: 'templates/tab-servo.html',
          controller: 'ServoCtrl'
        }
      }
    })

  .state('tab.sensors', {
    url: '/sensors',
    views: {
      'tab-sensors': {
        templateUrl: 'templates/tab-sensors.html',
        controller: 'SensorsCtrl'
      }
    }
  })

  .state('tab.motor', {
    url: '/motor',
    views: {
      'tab-motor': {
        templateUrl: 'templates/tab-motor.html',
        controller: 'MotorCtrl'
      }
    }
  })

  .state('tab.follow', {
    url: '/follow',
    views: {
      'tab-follow': {
        templateUrl: 'templates/tab-follow.html',
        controller: 'FollowCtrl'
      }
    }
  })

  .state('tab.settings', {
    url: '/settings',
    views: {
      'tab-settings': {
        templateUrl: 'templates/tab-settings.html',
        controller: 'SettingsCtrl'
      }
    }
  });

  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/tab/settings');

});
