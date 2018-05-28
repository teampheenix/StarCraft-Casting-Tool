var tweens = {};
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var myDefaultFont = null;
var data = {};
var font = "DEFAULT";
var padding = "2px";
var cssFile = "";
var tweens = {};
var tweenInitial = new TimelineMax();
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

function loadStoredData() {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-mapicons_box_' + ident.toString() + '-';
    data = JSON.parse(storage.getItem(key + 'data')) || {};
    font = storage.getItem(key + 'font');
    cssFile = storage.getItem(key + 'css');
    padding = storage.getItem(key + 'padding') || '2px';
    try {
      changeCSS(cssFile);
    } catch (e) {}

    try {
      setFont(font);
    } catch (e) {}

    try {
      setPadding(font);
    } catch (e) {}

  } catch (e) {}
}

function storeData(scope = null) {
  try {
    var storage = window.localStorage;
    var key = 'scct-' + profile + '-mapicons_box_' + ident.toString() + '-';
    if (scope == null || scope == "data") storage.setItem(key + 'data', JSON.stringify(data));
    if (scope == null || scope == "font") storage.setItem(key + 'font', font);
    if (scope == null || scope == "padding") storage.setItem(key + 'padding', padding);
    if (scope == null || scope == "css") storage.setItem(key + 'css', cssFile);
  } catch (e) {}
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
      changeScore(jsonObject.data.winner, jsonObject.data.setid, jsonObject.data.border_color, jsonObject.data.opacity);
    } else if (jsonObject.event == 'CHANGE_TEXT') {
      changeText(jsonObject.data.icon, jsonObject.data.label, jsonObject.data.text);
    } else if (jsonObject.event == 'CHANGE_RACE') {
      changeRace(jsonObject.data.icon, jsonObject.data.team, jsonObject.data.race);
    } else if (jsonObject.event == 'CHANGE_MAP') {
      changeMap(jsonObject.data.icon, jsonObject.data.map, jsonObject.data.map_img);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      setFont(jsonObject.data.font);
    } else if (jsonObject.event == 'CHANGE_PADDING') {
      setPadding(jsonObject.data.padding);
    } else if (jsonObject.event == 'DATA') {
      if (dataChanged(jsonObject.data)) {
        handleData();
      }
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
  newData = processData(newData);
  if (JSON.stringify(data) === JSON.stringify(newData)) {
    return false;
  } else {
    data = newData;
    storeData('data');
    return true;
  }
}

function processData(myData){
  var length = Object.keys(data).length;
  for(var i = 1; i<= length; i++){
    delete myData[i]['score_color'];
  }
  return myData;
}

function changeScore(winner, set, color, opacity) {
  var mapicon = $("#mapicon" + (set).toString());
  $(mapicon).find("div.image").css("border-color", color);
  $(mapicon).find("div.opa").css('opacity', opacity);
  data[set]['opacity'] = opacity;
  data[set]['border_color'] = color;
  if (winner == 0) {
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    data[set]['status1'] = '';
    data[set]['status2'] = '';
  } else if (winner == -1) {
    $(mapicon).find("div.player1").addClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    data[set]['status1'] = 'winner';
    data[set]['status2'] = 'loser';
  } else if (winner == 1) {
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").addClass('winner');
    data[set]['status1'] = 'loser';
    data[set]['status2'] = 'winner';
  }
  storeData('data');
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
  data[iconID]["race" + team.toString()] = race;
  storeData('data');
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
  data[iconID]['mapname'] = map;
  data[iconID]['map_img'] = map_img;
  storeData('data');
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

function setPadding(padding) {
  document.documentElement.style.setProperty('--padding', padding);
  storeData("padding");
}

function handleData(force = true) {
  if (initNeeded) {
    initNeeded = false;
    for (var i in data) {
      if ($('#mapicon' + i.toString()).length == 0) {
        $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
        var mapicon = "#mapicon" + i.toString();
        $(mapicon).load("data/mapicon-box-template.html", hideFill.bind(null, i));
      }
    }
  } else if (!tweenInitial.isActive() && force) {
    initNeeded = true;
    outroAnimation();
  } else if (force) {
    setTimeout(function() {
      handleData();
    }, 1000);
  }
}

function hideFill(i) {
  var mapicon = $("#mapicon" + i.toString());
  var race1 = mapicon.find("div.race1");
  var race2 = mapicon.find("div.race2");
  var vs = mapicon.find("div.vs");
  mapicon.css("opacity", "0.0");
  race1.css("opacity", "0.0");
  race2.css("opacity", "0.0");
  vs.css("opacity", "0.0");
  $(document).ready(function() {
    fillBox(i);
  });
}

function fillBox(i) {
  var mapicon = "#mapicon" + i.toString();
  var mapdata = data[i];
  var length = Object.keys(data).length;
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
  $(mapicon).ready(function() {
    $(mapicon).find(".text-fill").textfill();
    if (i == length) {
      $(mapicon).ready(function() {
        initAnimation();
      });
    }
  });
}

function initAnimation() {
  tweenInitial = new TimelineMax();
  var length = Object.keys(data).length;
  var mapicon_tweens = [];
  for (var i = 1; i <= length; i++) {
    var mapicon = $("#mapicon" + i.toString());
    var image = mapicon.find("div.image");
    var image = mapicon.find("div.image");
    var race1 = mapicon.find("div.race1");
    var race2 = mapicon.find("div.race2");
    var player1 = mapicon.find("div.player1");
    var player2 = mapicon.find("div.player2");
    var mapname = mapicon.find("div.upper-panel");
    var maplabel = mapicon.find("div.lower-panel");
    var vs = mapicon.find("div.vs");
    var local_tween = new TimelineMax();
    local_tween.to(mapicon, 0, {
        opacity: "1"
      })
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
    mapicon_tweens.push(local_tween);
  }
  tweenInitial.delay(0.3);
  tweenInitial.add(mapicon_tweens, "+=0", "sequence", -0.25);
}

function outroAnimation() {
  tweenInitial.eventCallback("onReverseComplete", refreshData);
  tweenInitial.delay(0);
  tweenInitial.reverse(0);
}

function refreshData() {
  $("#container").empty();
  handleData();
}
