var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var controller = new Controller(profile, 'ui_logo', ident);
init();

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

function connectWebsocket() {
  console.time('connectWebsocket');
  var path = "ui_logo_" + ident.toString();
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
      $('#img').attr("src", jsonObject.data.logo);
      $('body').css("display", jsonObject.data.display);
    }
  }

  socket.onclose = function(e) {
    console.timeEnd('connectWebsocket');
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function() {
      connectWebsocket();
    }, reconnectIntervalMs);
  }
}
