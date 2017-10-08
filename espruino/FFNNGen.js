/*
Simple JSFiddle that uses Synaptic to generate
a neural net based on the captured ground truth
from the five sensors.

Published under Creative Commons

Richard Hopkins, 8th October 2017
*/
var Neuron = synaptic.Neuron, // create synaptic objects
  Layer = synaptic.Layer,
  Network = synaptic.Network,
  Trainer = synaptic.Trainer,
  Architect = synaptic.Architect;
// create a feed forward neural net that takes
// input from the five sensors and outputs three variable
// the hidden layer has four neurons
var myFFNN = new Architect.Perceptron(5, 4, 3);
// create a trainer for the neural net
var FFNNtrainer = new Trainer(myFFNN);
/*
this is the training set that was automatically generated
by the program from the previous post
in reality there are around 6,000 lines of training data
from three separate runs of the ground truth generator
the inputs are the recorded state of the
five ultrasonic sensors, the outputs
are the sine, cosine and distance injected by the generator
*/
var myTrainingSet = [
{input:[1,0,0,0,0],output: [0.5,1,0.33333333]},
{input:[0,1,0,0,0],output: [0.5,1,0.33333333]},
{input:[1,0,0,0,0],output: [0.5,1,0.33333333]},
{input:[0,0,0,0,0],output: [0.98429158056,0.62434494358,0.66666667000]},
{input:[0,0,0,0,0],output: [0.98429158056,0.62434494358,0.66666667000]},
{input:[0,0,0,0,0],output: [0.98429158056,0.62434494358,0.66666667000]},
{input:[0,0,0,0,0],output: [0.93037101350,0.75452070787,1]},
{input:[0,0,0,0,0],output: [0.93037101350,0.75452070787,1]},
{input:[0,0,0,0,0],output: [0.93037101350,0.75452070787,1]},
{input:[0,0,0,0,0],output: [0.93037101350,0.75452070787,1]},
];
// this performs the training
// reducing the rate from the default of 0.01 to 0.001 made the biggest
// difference to accuracy; the other elements are default
FFNNtrainer.train(myTrainingSet, {
  rate: .001,
  iterations: 20000,
  error: .005,
  shuffle: true,
  log: 1000
});
// this generates the standalone function that can execute on the Espruino
var standalone = myFFNN.standalone();
// this sends that function to the console for cutting and pasting
// into the Espruino IDE
console.log(standalone.toString());
alert("Standalone network generated");
