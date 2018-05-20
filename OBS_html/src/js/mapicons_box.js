var tweens = {};
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var tweens = {};


init();

function init() {
  connectWebsocket();
  //changeCSS("src/css/mapicons_box/Square.css", 0);
  // for (i = 1; i <= 8; i++) {
  //         $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
  //         loadBox(i);
  // };
  // setTimeout(function() {
  //         hideBoxs();
  // }, 6000);
  // setTimeout(function() {
  //         $('#container').empty();
  //         for (i = 1; i <= 3; i++) {
  //                 $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
  //                 loadBox(i);
  //         };
  // }, 12000);
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
      changeScore(jsonObject.data.winner, jsonObject.data.setid, jsonObject.data.color);
    } else if (jsonObject.event == 'CHANGE_TEXT') {
      changeText(jsonObject.data.icon, jsonObject.data.label, jsonObject.data.text);
    } else if (jsonObject.event == 'CHANGE_BORDER_COLORS') {
      //setColors(jsonObject.data.color1, jsonObject.data.color2);
    } else if (jsonObject.event == 'CHANGE_FONT') {
      //setFont(jsonObject.data.font);
    } else if (jsonObject.event == 'DATA') {
      handleData(jsonObject.data);
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


function handleData(newData) {
  data = newData;
  for (var i in newData) {
    if ($('#mapicon' + i.toString()).length == 0) {
      $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
    }
    loadBox(i);
  }
}

function changeScore(winner, set, color) {
  var mapicon = $("#mapicon" + (set).toString());
  $(mapicon).find("div.image").css("border-color", color);
  console.log(winner);
  if(winner==0){
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
  }else if(winner==-1){
    $(mapicon).find("div.player1").addClass('winner');
    $(mapicon).find("div.player2").removeClass('winner');
  }else if(winner==1){
    $(mapicon).find("div.player1").removeClass('winner');
    $(mapicon).find("div.player2").addClass('winner');
  }
}

function changeText(iconID, label, new_value) {
  var icon = $('#mapicon' + iconID.toString());
  var id = iconID.toString()+label;
  var object = icon.find("span."+label);
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
      console.log(parent);
      parent.find(".text-fill").textfill({debug: true});
    });
  }
}

function showHide(i) {
  var mapicon = $("#mapicon" + i.toString());
  var image = mapicon.find("div.image");
  var race1 = mapicon.find("div.race-left");
  var race2 = mapicon.find("div.race-right");
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
    fillBox(i);
  });
}

function fillBox(i) {
  var mapicon = "#mapicon" + i.toString();
  var mapdata = data[i];
  $(mapicon).find("span.player1").text(mapdata['player1']);
  $(mapicon).find("div.player1").addClass(mapdata['status1']);
  $(mapicon).find("div.player2").addClass(mapdata['status2']);
  $(mapicon).find("span.player2").text(mapdata['player2']);
  $(mapicon).find("span.mapname").text(mapdata['map_name']);
  $(mapicon).find("span.maplabel").text(mapdata['map_id']);
  $(mapicon).find("div.race-left").attr("id", mapdata['race1']);
  $(mapicon).find("div.race-right").attr("id", mapdata['race2']);
  $(mapicon).find("div.image").css("border-color", mapdata['border_color']);
  $(mapicon).find("div.image").css("background-image", 'url("src/img/maps/' + mapdata['map_img'] + '")');
  $(mapicon).find(".text-fill").textfill();
  setTimeout(showBox.bind(null, i), 200 * (i - 1));
}

function showBox(i) {
  tweens[i] = new TimelineMax();
  var mapicon = $("#mapicon" + i.toString());
  var image = mapicon.find("div.image");
  var race1 = mapicon.find("div.race-left");
  var race2 = mapicon.find("div.race-right");
  var player1 = mapicon.find("div.player1");
  var player2 = mapicon.find("div.player2");
  var mapname = mapicon.find("div.upper-panel");
  var maplabel = mapicon.find("div.lower-panel");
  var vs = mapicon.find("div.vs");
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
  for (i = 1; i <= Object.keys(tweens).length; i++) {
    var timeout = 200 * (Object.keys(tweens).length - i);
    setTimeout(hideBox.bind(null, i), timeout);
  };
}

function hideBox(i) {
  console.log(i);
  tweens[i].reverse(0);
}

function loadBox(i) {
  mapicon = "#mapicon" + i.toString();
  $(mapicon).load("data/mapicon-box-template.html", showHide.bind(null, i));
}


function changeCSS(newCssFile) {
  console.log('CSS file changed to', newCssFile);
  $('link[rel="stylesheet"]').attr('href', newCssFile);

}
