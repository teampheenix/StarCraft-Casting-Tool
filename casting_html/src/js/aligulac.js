var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var controller = new Controller(profile, 'aligulac');
var texttween = new TimelineMax();
var tlv = new TimelineMax({
  paused: true,
  onUpdate: changeIt
});

init();

function changeIt() {
  p1 = (this.progress() * 100).toFixed(1);
  p2 = (100 - p1).toFixed(1);
  $('#precent_player1').text(p1 + '%');
  $('#precent_player2').text(p2 + '%');
}

function init() {
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
  connectWebsocket();
  loadStoredData();
}

function loadStoredData() {
  try {
    data = controller.loadData('data', true);
    if (data) {
      processData();
    }
  } catch (e) {}
}

function dataChanged(newData) {
  if (JSON.stringify(data) === JSON.stringify(newData)) {
    return false;
  } else {
    data = newData;
    storeData();
    return true;
  }
}

function storeData(scope = null) {
  if (scope == null || scope == "data") controller.storeData('data', data, true);
}

function processData() {
  var score_text = data['player1'] + ' ' + data['score1'] + '-' + data['score2'] + ' ' + data['player2'];
  var item = $('#score');
  if (texttween.isActive()) texttween.kill();
  texttween = new TimelineMax();
  texttween.to(item, 0.2, {
      opacity: 0
    })
    .call(_changeText, [item, score_text])
    .to(item, 0.2, {
      opacity: 1,
    }, "+=0.10");

  if (tlv.isActive()) {
    tlv.pause();
  }
  TweenLite.fromTo(tlv, 3, {
    progress: tlv.progress()
  }, {
    progress: data['prob1'],
    ease: Linear.easeNone
  });

  function _changeText(object, new_value) {
    object.text(new_value)
    $(document).ready(function() {
      $('#content').find(".text-fill").textfill({maxFontPixels: 80});
    });
  }
}

function connectWebsocket() {
  socket = new WebSocket(controller.generateKeyURI());

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event == 'DATA') {
      if (dataChanged(jsonObject.data)) processData();
    } else if (jsonObject.event == 'CHANGE_STYLE') {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      controller.setFont(jsonObject.data.font);
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
