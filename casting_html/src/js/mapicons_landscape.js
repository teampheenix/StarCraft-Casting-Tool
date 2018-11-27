var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var padding = "2px";
var tweens = {};
var tweenInitial = new TimelineMax();
var initNeeded = true;
var controller = new Controller(profile, 'mapicons_landscape', ident);

init();

function init() {
  loadStoredData();
  connectWebsocket();
  setTimeout(function() {
    handleData(false);
  }, 1000);
}

function storeData(scope = null) {
  if (scope == null || scope == "data") controller.storeData('data', data, true);
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    data = controller.loadData('data', true);
    setPadding(controller.loadData('padding') || '2px');
  } catch (e) {}
}

function connectWebsocket() {
  console.time('connectWebsocket');
  socket = new WebSocket(controller.generateKeyURI());

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event == 'CHANGE_STYLE') {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event == 'CHANGE_SCORE') {
      changeScore(jsonObject.data.winner, jsonObject.data.setid, jsonObject.data.score_color, jsonObject.data.opacity, jsonObject.data.hide);
    } else if (jsonObject.event == 'CHANGE_TEXT') {
      changeText(jsonObject.data.icon, jsonObject.data.label, jsonObject.data.text);
    } else if (jsonObject.event == 'CHANGE_RACE') {
      changeRace(jsonObject.data.icon, jsonObject.data.team, jsonObject.data.race);
    } else if (jsonObject.event == 'CHANGE_MAP') {
      changeMap(jsonObject.data.icon, jsonObject.data.map, jsonObject.data.map_img);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      controller.setFont(jsonObject.data.font);
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

function processData(myData) {
  for (var i in data) {
    try {
      delete myData[i]['border_color'];
    } catch (e) {}
  }
  return myData;
}

function changeScore(winner, set, color, opacity, hide) {
  var mapicon = $("#mapicon" + (set).toString());
  if (!mapicon.length) return;
  $(mapicon).find("div.circle").css("background-color", color);
  $(mapicon).find("div.opa").css('opacity', opacity);
  if (hide) {
    $(mapicon).find("div.circle").css('visibility', 'hidden');
  } else {
    $(mapicon).find("div.circle").css('visibility', 'visible');
  }
  data[set]['hide_scoreicon'] = hide;
  data[set]['opacity'] = opacity;
  data[set]['score_color'] = color;
  if (winner == 0) {
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    $(mapicon).find("div.player1").removeClass('loser');
    $(mapicon).find("div.player2").removeClass('loser');
    $(mapicon).find("div.race1").removeClass('winner');
    $(mapicon).find("div.race2").removeClass('winner');
    $(mapicon).find("div.race1").removeClass('loser');
    $(mapicon).find("div.race2").removeClass('loser');
    data[set]['status1'] = '';
    data[set]['status2'] = '';
  } else if (winner == -1) {
    $(mapicon).find("div.player1").removeClass('loser');
    $(mapicon).find("div.player1").addClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
    $(mapicon).find("div.player2").addClass('loser');
    $(mapicon).find("div.rac1").removeClass('loser');
    $(mapicon).find("div.race1").addClass('winner');
    $(mapicon).find("div.race2").removeClass('winner');
    $(mapicon).find("div.race2").addClass('loser');
    data[set]['status1'] = 'winner';
    data[set]['status2'] = 'loser';
  } else if (winner == 1) {
    $(mapicon).find("div.player2").removeClass('loser');
    $(mapicon).find("div.player2").addClass('winner');
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player1").addClass('loser');
    $(mapicon).find("div.race2").removeClass('loser');
    $(mapicon).find("div.race2").addClass('winner');
    $(mapicon).find("div.race1").removeClass('winner');
    $(mapicon).find("div.race1").addClass('loser');
    data[set]['status1'] = 'loser';
    data[set]['status2'] = 'winner';
  }
  storeData('data');
}

function changeText(iconID, label, new_value) {
  var icon = $('#mapicon' + iconID.toString());
  if (!icon.length) return;
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
      clearProps: "opacity"
    }, "+=0.15");

  function _changeText(parent, object, new_value) {
    object.text(new_value)
    parent.find(".text-fill").textfill({maxFontPixels: 80});
  }
}

function changeRace(iconID, team, race) {
  var icon = $('#mapicon' + iconID.toString());
  if (!icon.length) return;
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
  if (!icon.length) return;
  var box = icon.find("div.box");
  var image = icon.find("div.mapimg");
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
    if (map == "TBD" || map_img == 'TBD') {
      image.addClass('tbd');
      image.css("background-image", '');
    } else {
      image.removeClass('tbd');
      image.css("background-image", 'url("src/img/maps/' + map_img + '")');
    }
    parent.find(".text-fill").textfill({maxFontPixels: 80});
  }
}

function setPadding(newPadding) {
  if (padding != newPadding) {
    padding = newPadding;
    document.documentElement.style.setProperty('--padding', padding);
    storeData("padding");
  }
}


function handleData(force = true) {
  if (initNeeded) {
    initNeeded = false;
    for (var i in data) {
      if ($('#mapicon' + i.toString()).length == 0) {
        $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
        var mapicon = "#mapicon" + i.toString();
        $(mapicon).load("data/mapicon-landscape-template.html", hideFill.bind(null, i));
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
  var vs = mapicon.find("span.vs");
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
  var keys = Object.keys(data)
  var length = keys[keys.length - 1];
  $(mapicon).find("span.player1").text(mapdata['player1']);
  $(mapicon).find("div.player1").addClass(mapdata['status1']);
  $(mapicon).find("div.player2").addClass(mapdata['status2']);
  $(mapicon).find("div.race1").addClass(mapdata['status1']);
  $(mapicon).find("div.race2").addClass(mapdata['status2']);
  $(mapicon).find("span.player2").text(mapdata['player2']);
  $(mapicon).find("span.mapname").text(mapdata['mapname']);
  $(mapicon).find("span.maplabel").text(mapdata['maplabel']);
  $(mapicon).find("div.race1").attr("id", mapdata['race1']);
  $(mapicon).find("div.race2").attr("id", mapdata['race2']);
  $(mapicon).find("div.circle").css("background-color", mapdata['score_color']);
  if (mapdata['hide_scoreicon']) {
    $(mapicon).find("div.circle").css('visibility', 'hidden');
  } else {
    $(mapicon).find("div.circle").css('visibility', 'visible');
  }
  var image = $(mapicon).find("div.mapimg");
  if (mapdata['mapname'] == "TBD" || mapdata['map_img'] == 'TBD') {
    image.addClass('tbd');
    image.css("background-image", '');
  } else {
    image.removeClass('tbd');
    image.css("background-image", 'url("src/img/maps/' + mapdata['map_img'] + '")');
  }
  $(mapicon).find("div.opa").css('opacity', mapdata['opacity']);
  $(document).ready(function() {
    $(mapicon).find(".text-fill").textfill({maxFontPixels: 80});
    if (i == length) {
      $(mapicon).ready(function() {
        initAnimation();
      });
    }
  });
}

function initAnimation() {
  tweenInitial = new TimelineMax();
  var mapicon_tweens = [];
  for (var i in data) {
    var mapicon = $("#mapicon" + i.toString());
    var image = mapicon.find("div.box");
    var race1 = mapicon.find("div.race1");
    var race2 = mapicon.find("div.race2");
    var player1 = mapicon.find("div.player1");
    var player2 = mapicon.find("div.player2");
    var lowertext = mapicon.find("div.lower-text");
    var vs = mapicon.find("span.vs");
    var local_tween = new TimelineMax();
    local_tween.to(mapicon, 0, {
        opacity: "1"
      })
      .from(image, 0.30, {
        scaleX: 0.0,
        ease: Sine.easeInOut
      })
      .staggerFrom(lowertext, 0.15, {
        opacity: "0.0",
        y: '+=100%'
      }, 0.0)
      .staggerTo([vs, [race1, race2]], 0.15, {
        clearProps: "opacity"
      }, 0.20, '=-0.05')
      .from(player1, 0.20, {
        x: '-=110%'
      }, '=-0.20')
      .from(player2, 0.20, {
        x: '+=110%'
      }, '=-0.20');
    mapicon_tweens.push(local_tween);
  }
  tweenInitial.delay(0.3);
  tweenInitial.add(mapicon_tweens, "+=0", "sequence", -0.40);
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
