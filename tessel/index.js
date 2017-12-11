'use strict';

// Import the interface to Tessel hardware
var tessel = require('tessel');
var VL53L0X = require('tessel-vl53l0x');

var _vl53l0l = new VL53L0X(tessel.port.A);

_vl53l0l.setSignalRateLimit(.05, () => {
	_vl53l0l.startCapture();
});

_vl53l0l.on('distance', function(data){
	console.log("L: " + data);
});
