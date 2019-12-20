var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var initNeeded = true;
var padding = "2px";
var tweens = {};
var tweenInitial = new TimelineMax();
var controller = new Controller(profile, "vetoes");

init();

function init() {
  loadStoredData();
  connectWebsocket();
  setTimeout(function() {
    handleData(false);
  }, 1000);
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    data = controller.loadData("data", true);
    setPadding(controller.loadData("padding") || "2px");
  } catch (e) {}
}

function storeData(scope = null) {
  if (scope == null || scope === "data") {
    controller.storeData("data", data, true);
  }
}


function dataChanged(newData) {
  if (JSON.stringify(data) === JSON.stringify(newData)) {
    return false;
  } else {
    data = newData;
    storeData("data");
    return true;
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
    if (jsonObject.event === "DATA") {
      console.log(jsonObject.data);
      if (dataChanged(jsonObject.data)) {
        handleData();
      }
    } else if(jsonObject.event === "VETO"){
      handleVeto(jsonObject.data);
    } else if (jsonObject.event === "CHANGE_PADDING") {
      setPadding(jsonObject.data.padding);

    } else if (jsonObject.event === "CHANGE_STYLE") {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event === "CHANGE_FONT") {
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

function handleVeto(jsonData){
  let iconID = jsonData.idx;
  let icon = $("#veto" + iconID.toString());
  if (!icon.length) {
    return;
  }
  let veto_container = icon.find("div.veto_container");
  let id = iconID.toString() + "veto";
  data[iconID]["map_name"] = jsonData.map_name;
  data[iconID]["map_img"] = jsonData.map_img;
  data[iconID]["team"] = jsonData.team;
  storeData("data");
  if (tweens[id] && tweens[id].isActive()) {
    tweens[id].kill();
  }
  tweens[id] = new TimelineMax();
  tweens[id].to(veto_container, 0.35, {
      scaleX: 0.0,
      ease: Sine.easeInOut
    })
    .call(insertData, [iconID])
    .to(veto_container, 0.0, {
      clearProps: "scaleX"
    })
    .to(veto_container, 0.0, {
        scaleX: 0.0
      })
    .to(veto_container, 0.35, {
      scaleX: 1.0,
      ease: Sine.easeInOut
    }, "+=0.25");
}

function handleData(force = true) {
  if (initNeeded) {
    initNeeded = false;
    for (var i in data) {
      if ($("#veto" + i.toString()).length === 0) {
        $("#container").append("<div class='block' id='veto" + i.toString() + "'></div>");
        var mapicon = "#veto" + i.toString();
        $(mapicon).load("data/veto-template.html", hideFill.bind(null, i));
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
  var icon = $("#veto" + i.toString());
  icon.css("opacity", "0.0");
  $(document).ready(function() {
    fillBox(i);
  });
}

function insertData(i){
  let icon = "#veto" + i.toString();
  let vetodata = data[i];
  if(vetodata['team'] == 0){
    $(icon).find("div.veto_container").addClass("team1");
    $(icon).find("div.veto_container").removeClass("team2");
  }else{
    $(icon).find("div.veto_container").addClass("team2");
    $(icon).find("div.veto_container").removeClass("team1");
  }

  $(icon).find("div.mapname > span").text(vetodata["map_name"]);
  $(icon).find(".text-fill").textfill({
    maxFontPixels: 80
  });
  var image = $(icon).find("div.map");
  if (vetodata["map_name"] === "TBD" || vetodata["map_img"] === "TBD") {
    image.addClass("tbd");
    $(icon).find("div.veto_container").addClass("tbd");
    image.css("background-image", "");
  } else {
    image.removeClass("tbd");
    $(icon).find("div.veto_container").removeClass("tbd");
    image.css("background-image", 'url("src/img/maps/' + vetodata['map_img'] + '")');
  }
}

function fillBox(i) {
  let icon = "#veto" + i.toString();
  let keys = Object.keys(data)
  let length = keys[keys.length - 1];
  insertData(i);
  $(document).ready(function() {
    $(icon).find(".text-fill").textfill({
      maxFontPixels: 80
    });
    if (i === length) {
      $(icon).ready(function() {
        initAnimation();
      });
    }
  });
}

function initAnimation() {
  tweenInitial = new TimelineMax();
  var icon_tweens = [];
  for (var i in data) {
    var icon = $("#veto" + i.toString());
    var veto_container = icon.find("div.veto_container");
    var veto = icon.find("div.veto");
    var mapname = icon.find("div.mapname");
    var local_tween = new TimelineMax();
    local_tween.to(icon, 0, {
        opacity: "1"
      })
      .from(veto_container, 0.30, {
        scaleX: 0.0,
        ease: Sine.easeInOut
      })
      .staggerFrom([veto, mapname], 0.15, {
        opacity: 0.0
      }, 0.20, "=-0.05");
    icon_tweens.push(local_tween);
  }
  tweenInitial.delay(0.3);
  tweenInitial.add(icon_tweens, "+=0", "sequence", 0.25);
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

function setPadding(newPadding) {
  if (padding !== newPadding) {
    padding = newPadding;
    document.documentElement.style.setProperty("--padding", padding);
    storeData("padding");
  }
}
