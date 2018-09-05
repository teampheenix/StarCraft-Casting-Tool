var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var controller = new Controller(profile, 'aligulac');
init();

var tlv = new TimelineMax({
  paused: true,
  onUpdate: changeIt
});

tlv.fromTo("#player1", 1, {
    width: '0%'
  }, {
    width: '100%',
    ease: Linear.easeNone
  })
  .fromTo("#player2", 1, {
    width: '100%'
  }, {
    width: '0%',
    ease: Linear.easeNone
  }, '-=1');
tlv.seek(0.5);

function changeIt() {
  p1 = (this.progress() * 100).toFixed(1);
  p2 = (100 - p1).toFixed(1);
  $('#player1').html(p1 + '%');
  $('#player2').html(p2 + '%');
}

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

function processData(data) {
  if (tlv.isActive()) {
    tlv.pause()
  }
  TweenLite.fromTo(tlv, 3, {
    progress: tlv.progress()
  }, {
    progress: data['prob1'],
    ease: Linear.easeNone
  });
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
