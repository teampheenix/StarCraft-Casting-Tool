var tweens = {};
var socket = null;
var isopen = false;
var myDefaultFont = null;
var reconnectIntervalMs = 5000;
var data = {};
var font = "DEFAULT";
var cssFile = "";
var initNeeded = true;
var tweenInitial = new TimelineMax();
var tweens = {};

init();

function init() {
  myDefaultFont = getComputedStyle(document.body).getPropertyValue('--font');
  loadStoredData();
  initHide();
  connectWebsocket();
  setTimeout(function() {
    initAnimation(false);
  }, 1000);
}

function connectWebsocket() {
  console.time('connectWebsocket');
  path = "score"
  port = parseInt("0x".concat(profile), 16);
  socket = new WebSocket("ws://127.0.0.1:".concat(port, "/", path));

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event == 'CHANGE_STYLE') {
      changeCSS(jsonObject.data.file);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      setFont(jsonObject.data.font);
    } else if (jsonObject.event == 'ALL_DATA') {
      if (dataChanged(jsonObject.data)) {
        initAnimation();
      }
    } else if (jsonObject.event == 'CHANGE_TEXT') {
      changeText(jsonObject.data.id, jsonObject.data.text);
    } else if (jsonObject.event == 'CHANGE_IMAGE') {
      changeImage(jsonObject.data.id, jsonObject.data.img);
    } else if (jsonObject.event == 'CHANGE_SCORE') {
      changeScoreIcon(jsonObject.data.teamid, jsonObject.data.setid, jsonObject.data.color);
    } else if (jsonObject.event == 'SET_WINNER') {
      setWinner(jsonObject.data);
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


function dataChanged(newData) {
  if (JSON.stringify(data) === JSON.stringify(newData)) {
    return false;
  } else {
    data = newData;
    return true;
  }

}

function storeData(scope = null) {
  try {
    var storage = window.localStorage;
    if (scope == null || scope == "data") storage.setItem('scct-' + profile + '-score-data', JSON.stringify(data));
    if (scope == null || scope == "font") storage.setItem('scct-' + profile + '-score-font', font);
    if (scope == null || scope == "css") storage.setItem('scct-' + profile + '-score-css', cssFile);
  } catch (e) {}
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    data = JSON.parse(storage.getItem('scct-' + profile + '-score-data'));
    font = storage.getItem('scct-' + profile + '-score-font');
    cssFile = storage.getItem('scct-' + profile + '-score-css');
    if (data == null) data = {};
    try {
      changeCSS(cssFile);
    } catch (e) {}

    try {
      setFont(font);
    } catch (e) {}

  } catch (e) {}
}

function insertData() {
  storeData('data');
  $('#team1').text(data['team1']);
  $('#team2').text(data['team2']);
  $('#score1').text(data['score1']);
  $('#score2').text(data['score2']);
  $('#logo1').css("background-image", "url('../" + data['logo1'] + "')");
  $('#logo2').css("background-image", "url('../" + data['logo2'] + "')");
  if (data['winner'][0]) {
    $('#team1').addClass('winner');
    $('#team2').addClass('loser');
  } else {
    $('#team1').removeClass('winner');
  }
  if (data['winner'][1]) {
    $('#team2').addClass('winner');
    $('#team1').addClass('loser');
  } else {
    $('#team2').removeClass('winner');
  }
  if (!(data['winner'][0] || data['winner'][1])) {
    $('#team1').removeClass('winner');
    $('#team1').removeClass('loser');
    $('#team2').removeClass('winner');
    $('#team2').removeClass('loser');
  }
  insertIcons();
  $(document).ready(function() {
    $('#content').find(".text-fill").textfill();
  });
}

function setWinner(winner) {
  if (winner == 0) {
    $('#team1').removeClass('winner');
    $('#team2').removeClass('winner');
    $('#team1').removeClass('loser');
    $('#team2').removeClass('loser');
    data['winner'][0] = false;
    data['winner'][1] = false;
  } else if (winner == 1) {
    $('#team2').removeClass('loser');
    $('#team2').addClass('winner');
    $('#team1').removeClass('winner');
    $('#team1').addClass('loser');
    data['winner'][0] = false;
    data['winner'][1] = true;
  } else if (winner == -1) {
    $('#team1').removeClass('loser');
    $('#team1').addClass('winner');
    $('#team2').removeClass('winner');
    $('#team2').addClass('loser');
    data['winner'][0] = true;
    data['winner'][1] = false;
  }
  storeData('data');
}

function insertIcons() {
  for (var j = 0; j < 2; j++) {
    $('#score' + (j + 1).toString() + '-box').empty();
  }
  try {
    for (var i = 0; i < Object.keys(data['sets']).length; i++) {
      for (var j = 0; j < 2; j++) {
        var color = data['sets'][i][j];
        $('#score' + (j + 1).toString() + '-box').append('<div class="circle" id="circle-' + (j + 1).toString() + '-' + (i + 1).toString() + '" style="background-color: ' + color + '"></div>');
      }
    }
  } catch (e) {}
}

function changeCSS(newCssFile) {
  if (newCssFile && newCssFile != "null") {
    cssFile = newCssFile;
    console.log('CSS file changed to', newCssFile);
    $('link[rel="stylesheet"]').attr('href', newCssFile);
    storeData("css");
    $(document).ready(function() {
      $('#content').find(".text-fill").textfill();
    });
  }
}

function initHide() {
  var content = document.getElementById("content");
  content.style.setProperty('visibility', 'visible');
  tweenInitial.staggerTo([content], 0, {
    opacity: "0"
  }, 0);
}

function initAnimation(force = true) {
  if (!tweenInitial.isActive() && initNeeded) {
    insertData();
    tweenInitial = new TimelineMax();
    tweenInitial.delay(0.5)
      .fromTo([$('#content')], 0, {
        opacity: "0"
      }, {
        opacity: "1"
      }, 0)
      .fromTo($('#box'), 0.35, {
        scaleY: 0.0,
        force3D: true
      }, {
        scaleY: 1.0,
        force3D: true
      })
      .staggerFromTo([$('#logo1'), $('#logo2')], 0.35, {
        scale: 0.0,
        force3D: true
      }, {
        scale: 1.0,
        force3D: true
      }, 0, '-=0.1')
      .staggerFromTo([
        [$('#team1'), $('#team2')], $('#score'), [$('#score1'), $('#score2')]
      ], 0.35, {
        opacity: '0'
      }, {
        opacity: '1'
      }, 0.10, '-=0.35')
      .staggerFromTo([$('#score1-box > div.circle'), $('#score2-box > div.circle')], 0.25, {
        scale: 0.0,
        opacity: '0',
        force3D: true
      }, {
        scale: 1.0,
        opacity: '1',
        force3D: true
      }, 0.0, '-=0.50');
    initNeeded = false;
  } else if (force && !tweenInitial.isActive()) {
    outroAnimation();
  } else if (force) {
    setTimeout(function() {
      initAnimation();
    }, 1000);
  }
}

function outroAnimation() {
  if (!tweenInitial.isActive() && tweenInitial.progress() == 1) {
    tweenInitial.eventCallback("onReverseComplete", initAnimation);
    tweenInitial.delay(0);
    tweenInitial.reverse(0);
    initNeeded = true;
  }
}

function changeText(id, new_value) {
  var object = $('#' + id);
  if (id == 'score1' || id == 'score2') {
    new_data_value = parseInt(new_value);
  } else {
    new_data_value = new_value;
  }
  if (data[id] == new_value) {
    return;
  } else {
    data[id] = new_data_value;
    storeData('data');
  }

  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(object, 0.25, {
      opacity: 0
    })
    .call(_changeText, [object, new_value])
    .to(object, 0.25, {
      opacity: 1
    }, "+=0.15");

  function _changeText(object, new_value) {
    object.text(new_value)
    $(document).ready(function() {
      $('#content').find(".text-fill").textfill();
    });
  }
}

function changeImage(id, new_value) {
  var object = $('#' + id);
  if (data[id] == new_value) {
    return;
  } else {
    data[id] = new_value;
    storeData('data');
  }
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(object, 0.35, {
      scale: 0,
      force3D: true
    })
    .call(_changeImage, [object, new_value])
    .to(object, 0.35, {
      scale: 1,
      force3D: true
    }, "+=0.25");

  function _changeImage(object, new_value) {
    object.css("background-image", "url('../" + new_value + "')");
  }
}


function changeScoreIcon(team, set, color) {
  var id = '#circle-' + team.toString() + '-' + set.toString();
  var object = $(id);
  if (data['sets'][set - 1][team - 1] == color) {
    return;
  } else {
    data['sets'][set - 1][team - 1] = color;
    storeData('data');
  }
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(object, 0.15, {
      scale: 0,
      opacity: '0',
      force3D: true
    })
    .call(_changeIcon, [object, color])
    .to(object, 0.15, {
      scale: 1,
      opacity: '1',
      force3D: true
    }, "+=0.05");

  function _changeIcon(object, new_value) {
    object.css("background-color", new_value);
  }
}

function setFont(newFont) {
  if (newFont == 'DEFAULT') {
    newFont = myDefaultFont;
  }
  font = newFont.trim();
  document.documentElement.style.setProperty('--font', font);
  storeData("font");
}
