var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var controller = new Controller(profile, 'aligulac');
init();
$('#player1').resize(function(){
    var elem = $(this);

});

function init() {
  // loadStoredData();
  connectWebsocket();
}

function loadStoredData() {
  data = controller.loadData('data', true);
}

function storeData(scope = null) {
  if (scope == null || scope == "data") controller.storeData('data', data, true);
}

function processData(data){
    var width1 = (data['prob1']*100).toFixed(2) + '%';
    var width2 = (data['prob2']*100).toFixed(2) + '%';
    console.log(width1, width2);
    $('#player1').css('width', width1);
    $('#player1').html(width1);
    $('#player2').css('width', width2);
    $('#player2').html(width2);
}

function connectWebsocket() {
  var path = "aligulac";
  var port = parseInt("0x".concat(profile), 16);
  socket = new WebSocket("ws://127.0.0.1:".concat(port, "/", path));

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event == 'DATA') {
      console.log(jsonObject.data);
      processData(jsonObject.data);
    }
  }

  socket.onclose = function(e) {
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function() {
      connectWebsocket();
    }, reconnectIntervalMs);
  }
}
