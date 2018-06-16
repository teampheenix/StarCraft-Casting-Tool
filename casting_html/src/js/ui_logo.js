var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};

init();

function init() {
  // loadStoredData();
  connectWebsocket();
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-ui_logo_' + ident.toString() + '-';
    data = JSON.parse(storage.getItem(key + 'data')) || {};
  } catch (e) {}
}

function storeData(scope = null) {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-ui_logo_' + ident.toString() + '-';
    if (scope == null || scope == "data") storage.setItem(key + 'data', JSON.stringify(data));
  } catch (e) {}
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
