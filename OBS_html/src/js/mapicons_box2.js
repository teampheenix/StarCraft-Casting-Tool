var tweens = {};
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var myDefaultFont = null;
var data = {};
var font = "DEFAULT";
var cssFile = "";
var tweens = {};
var isLocked = false;
var initNeeded = true;

init();

function init() {
  myDefaultFont = getComputedStyle(document.body).getPropertyValue('--font');
  loadStoredData();
  connectWebsocket();
  setTimeout(function() {
    handleData(false);
  }, 1000);
}

function connectWebsocket() {
  console.time('connectWebsocket');
  var path = "mapicons_box_" + ident.toString();
  var port = parseInt("0x".concat(profile), 16);
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
    } else if (jsonObject.event == 'CHANGE_SCORE') {
      changeScore(jsonObject.data.winner, jsonObject.data.setid, jsonObject.data.color, jsonObject.data.opacity);
    } else if (jsonObject.event == 'CHANGE_TEXT') {
      changeText(jsonObject.data.icon, jsonObject.data.label, jsonObject.data.text);
    } else if (jsonObject.event == 'CHANGE_RACE') {
      changeRace(jsonObject.data.icon, jsonObject.data.team, jsonObject.data.race);
    } else if (jsonObject.event == 'CHANGE_MAP') {
      changeMap(jsonObject.data.icon, jsonObject.data.map, jsonObject.data.map_img);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      setFont(jsonObject.data.font);
    } else if (jsonObject.event == 'DATA') {
      handleData(false, jsonObject.data);
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

function storeData(scope = null) {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-mapicons_box_' + ident.toString() + '-';
    if (scope == null || scope == "data") storage.setItem(key + 'data', JSON.stringify(data));
    if (scope == null || scope == "font") storage.setItem(key + 'font', font);
    if (scope == null || scope == "css") storage.setItem(key + 'css', cssFile);
  } catch (e) {}
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-mapicons_box_' + ident.toString() + '-';
    data = JSON.parse(storage.getItem(key + 'data'));
    font = storage.getItem(key + 'font');
    cssFile = storage.getItem(key + 'css');
    if (data == null) data = {};
    try {
      changeCSS(cssFile);
    } catch (e) {}

    try {
      setFont(font);
    } catch (e) {}

  } catch (e) {}
}


function handleData(force = true, newData = null) {
  if (force || !isLocked) {
    isLocked = true;
    console.log("locked.")
    if (newData != null) {
      data = newData;
      storeData('data');
    }
    if (!initNeeded) {
      hideBoxs();
    } else {
      var length = Object.keys(data).length;
      for (var i in data) {
        if ($('#mapicon' + i.toString()).length == 0) {
          $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
        }
        if (i == length) {
          console.log("Starting tween "+i.toString()+" with lock");
          loadBox(i, unlock);
        } else {
          console.log("Starting tween "+i.toString()+" withoutlock");
          loadBox(i);
        }
      }
    }
  }
}

function unlock() {
  isLocked = false;
  initNeeded = false;
  console.log("unlocked.")
}

function changeScore(winner, set, color, opacity) {
  var mapicon = $("#mapicon" + (set).toString());
  $(mapicon).find("div.image").css("border-color", color);
  $(mapicon).find("div.opa").css('opacity', opacity);
  data[set]['opacity'] = opacity;
  storeData('data');
  if (winner == 0) {
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    data[set]['status1'] = '';
    data[set]['status2'] = '';
  } else if (winner == -1) {
    $(mapicon).find("div.player1").addClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    data[set]['status1'] = 'winner';
    data[set]['status2'] = '';
  } else if (winner == 1) {
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").addClass('winner');
    data[set]['status1'] = '';
    data[set]['status2'] = 'winner';
  }
}

function changeText(iconID, label, new_value) {
  var icon = $('#mapicon' + iconID.toString());
  var id = iconID.toString() + label;
  var object = icon.find("span." + label);
  data[iconID][label] = new_value;
  storeData('data');
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(object, 0.25, {
      opacity: 0
    })
    .call(_changeText, [icon, object, new_value])
    .to(object, 0.25, {
      opacity: 1
    }, "+=0.15");

  function _changeText(parent, object, new_value) {
    object.text(new_value)
    $(document).ready(function() {
      parent.find(".text-fill").textfill();
    });
  }
}

function changeRace(iconID, team, race) {
  var icon = $('#mapicon' + iconID.toString());
  var id = iconID.toString() + "race" + team.toString();
  var object = icon.find("div.race" + team.toString());
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(object, 0.35, {
      scale: 0,
      force3D: true
    })
    .call(_changeRace, [object, race])
    .to(object, 0.35, {
      scale: 1,
      force3D: true
    }, "+=0.25");

  function _changeRace(object, race) {
    object.attr("id", race);
  }
}

function changeMap(iconID, map, map_img) {
  var icon = $('#mapicon' + iconID.toString());
  var image = icon.find("div.image");
  var name = icon.find("span.mapname")
  var id = iconID.toString() + "map";
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(icon, 0.35, {
      scale: 0,
      force3D: true
    })
    .call(_changeMap, [icon, image, name, map, map_img])
    .to(icon, 0.35, {
      scale: 1,
      force3D: true
    }, "+=0.25");

  function _changeMap(parent, image, name, map, map_img) {
    name.text(map);
    image.css("background-image", 'url("src/img/maps/' + map_img + '")');
    $(document).ready(function() {
      parent.find(".text-fill").textfill();
    });
  }
}

function showHide(i, callback = null) {
  var mapicon = $("#mapicon" + i.toString());
  var image = mapicon.find("div.image");
  var race1 = mapicon.find("div.race1");
  var race2 = mapicon.find("div.race2");
  var player1 = mapicon.find("div.player1");
  var player2 = mapicon.find("div.player2");
  var mapname = mapicon.find("div.upper-panel");
  var maplabel = mapicon.find("div.lower-panel");
  var vs = mapicon.find("div.vs");
  mapicon.css("opacity", "0.0");
  race1.css("opacity", "0.0");
  race2.css("opacity", "0.0");
  vs.css("opacity", "0.0");
  $(document).ready(function() {
    fillBox(i, callback);
  });
}

function fillBox(i, callback = null) {
  var mapicon = "#mapicon" + i.toString();
  var mapdata = data[i];
  $(mapicon).find("span.player1").text(mapdata['player1']);
  $(mapicon).find("div.player1").addClass(mapdata['status1']);
  $(mapicon).find("div.player2").addClass(mapdata['status2']);
  $(mapicon).find("span.player2").text(mapdata['player2']);
  $(mapicon).find("span.mapname").text(mapdata['mapname']);
  $(mapicon).find("span.maplabel").text(mapdata['maplabel']);
  $(mapicon).find("div.race1").attr("id", mapdata['race1']);
  $(mapicon).find("div.race2").attr("id", mapdata['race2']);
  $(mapicon).find("div.image").css("border-color", mapdata['border_color']);
  $(mapicon).find("div.image").css("background-image", 'url("src/img/maps/' + mapdata['map_img'] + '")');
  $(mapicon).find("div.opa").css('opacity', mapdata['opacity']);
  $(mapicon).find(".text-fill").textfill();
  setTimeout(showBox.bind(null, i, callback), 200 * (i - 1));
}

function showBox(i, callback = null) {
  tweens[i] = new TimelineMax();
  var mapicon = $("#mapicon" + i.toString());
  var image = mapicon.find("div.image");
  var race1 = mapicon.find("div.race1");
  var race2 = mapicon.find("div.race2");
  var player1 = mapicon.find("div.player1");
  var player2 = mapicon.find("div.player2");
  var mapname = mapicon.find("div.upper-panel");
  var maplabel = mapicon.find("div.lower-panel");
  var vs = mapicon.find("div.vs");

  if (callback != null) {
    tweens[i].eventCallback("onComplete", callback);
  }
  tweens[i].delay(0.5)
    .staggerTo([mapicon], 0, {
      opacity: "1"
    }, 0.1)
    .from(image, 0.35, {
      width: "0%",
      border: "0px",
      left: "50%",
      ease: Sine.easeInOut
    })
    .staggerFrom([mapname, maplabel], 0.2, {
      opacity: "0.0",
      height: "0px"
    }, 0.0)
    .staggerTo([vs, [race1, race2]], 0.2, {
      opacity: "1.0"
    }, 0.20, '=-0.2')
    .from(player1, 0.15, {
      x: '-=110%'
    }, '=-0.15')
    .from(player2, 0.15, {
      x: '+=110%'
    }, '=-0.15');
}

function hideBoxs() {
  initNeeded = true;
  for (i = 1; i <= Object.keys(tweens).length; i++) {
    var timeout = 200 * (Object.keys(tweens).length - i);
    if (i == 1) {
      setTimeout(hideBox.bind(null, i, handleData), timeout);
    } else {
      setTimeout(hideBox.bind(null, i), timeout);
    }
  };
}

function hideBox(i, callback = null) {
  if (callback != null) {
    console.log("Register callback for " + i.toString());
    tweens[i].eventCallback("onReverseComplete", callback);
  }
  tweens[i].delay(0.2);
  tweens[i].reverse(0);
}

function loadBox(i, callback = null) {
  mapicon = "#mapicon" + i.toString();
  $(mapicon).load("data/mapicon-box-template.html", showHide.bind(null, i, callback));
}

function changeCSS(newCssFile) {
  if (newCssFile && newCssFile != "null") {
    cssFile = newCssFile;
    console.log('CSS file changed to', newCssFile);
    $('link[rel="stylesheet"]').attr('href', newCssFile);
    storeData("css");
  }
}

function setFont(newFont) {
  if (newFont == 'DEFAULT') {
    newFont = myDefaultFont;
  }
  font = newFont.trim();
  document.documentElement.style.setProperty('--font', font);
  storeData("font");
  $(document).ready(function() {
    $('#container').find(".text-fill").textfill();
  });
}
