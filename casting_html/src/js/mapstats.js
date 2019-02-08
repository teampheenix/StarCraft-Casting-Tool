var data = {};
var tweenShowMap = new TimelineMax({
  paused: true
});
var tweenInitial = new TimelineMax();
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var myDefaultFont = null;
var initNeeded = true;
var storage = null;
var mapData = {};
var colors = {};
var currentMap = "";

var controller = new Controller(profile, "mapstats");

// Warn if overriding existing method
if (Array.prototype.equals)
  console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
// attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function(array) {
  // if the other array is a falsy value, return
  if (!array)
    return false;

  // compare lengths - can save a lot of time
  if (this.length !== array.length)
    return false;

  for (var i = 0, l = this.length; i < l; i++) {
    // Check if we have nested arrays
    if (this[i] instanceof Array && array[i] instanceof Array) {
      // recurse into the nested arrays
      if (!this[i].equals(array[i]))
        return false;
    } else if (this[i] !== array[i]) {
      // Warning - two different object instances will never be equal: {x:20} != {x:20}
      return false;
    }
  }
  return true;
}
// Hide method from for-in loops
Object.defineProperty(Array.prototype, "equals", {
  enumerable: false
});

init();

function init() {
  loadStoredData();
  initHide();
  connectWebsocket();
  if (Object.keys(mapData).length > 0) initAnimation(getCurrentMap());
}

function getCurrentMap() {
  if (currentMap === "" || currentMap == undefined || !Object.keys(mapData).includes(currentMap)) {
    try {
      currentMap = Object.keys(mapData)[0];
    } catch (e) {
      currentMap = "";
    }

  }
  if (currentMap == undefined) currentMap = "";
  return currentMap;

}

function storeData(scope = null) {
  if (scope == null || scope === "mapdata") controller.storeData("data", mapData, true);
  if (scope == null || scope === "colors") controller.storeData("colors", colors, true);
  if (scope == null || scope === "currentmap") controller.storeData("currentmap", currentMap);
}

function loadStoredData() {
  try {
    var storage = window.localStorage;
    mapData = controller.loadData("mapdata", true);
    colors = controller.loadData("colors", true);
    currentMap = controller.loadData("currentmap");
    if (currentMap == null) currentMap = "";
    if (colors == null) colors = {};
    if (mapData == null) mapData = {};
    try {
      setColors(colors["color1"], colors["color2"]);
    } catch (e) {}
    loadImages();
    addMaps();
  } catch (e) {}
}


function connectWebsocket() {
  console.time("connectWebsocket");
  socket = new WebSocket(controller.generateKeyURI());
  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event === "CHANGE_STYLE") {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event === "CHANGE_COLORS") {
      setColors(jsonObject.data.color1, jsonObject.data.color2);
    } else if (jsonObject.event === "CHANGE_FONT") {
      controller.setFont(jsonObject.data.font);
    } else if (jsonObject.event === "MAPSTATS") {
      var doInit = Object.keys(mapData).length === 0;
      select = jsonObject.data.map;
      change = newMapData(jsonObject.data.maps);
      if (doInit) {
        addMaps();
        if (select !== "") {
          initAnimation(select);
        } else {
          initAnimation(getCurrentMap());
        }
      } else {
        if (change) {
          currentMap = select;
          outroAnimation();
        } else {
          markMaps();
        }
        if (select !== getCurrentMap()) {
          self.selectMap(select);
        }
      }
    } else if (jsonObject.event === "SELECT_MAP") {
      if (jsonObject.data.map !== getCurrentMap()) {
        self.selectMap(jsonObject.data.map, jsonObject.data.played, jsonObject.data.vetoed);
      }
    } else if (jsonObject.event === "MARK_PLAYED") {
      markPlayed(jsonObject.data.map, jsonObject.data.played);
    } else if (jsonObject.event === "MARK_VETOED") {
      markVetoed(jsonObject.data.map, jsonObject.data.vetoed);
    } else if (jsonObject.event === "DEBUG_MODE") {}
  }

  socket.onclose = function(e) {
    console.timeEnd("connectWebsocket");
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function() {
      connectWebsocket();
    }, reconnectIntervalMs);
  }
}

function newMapData(newData) {
  var change = false;
  if (!Object.keys(newData).equals(Object.keys(mapData))) {
    change = true;
  }
  mapData = newData;
  loadImages();
  storeData("mapdata");
  return change;
}

function loadImages() {
  for (var name in mapData) {
    mapData[name]["image"] = new Image();
    mapData[name]["image"].src = "src/img/maps/".concat(name.replace(/\s/g, "_"), ".jpg");
  }
}

function addMaps() {
  removeMaps();
  for (var name in mapData) {
    addMap(name, mapData[name]["played"], mapData[name]["vetoed"]);
  }
}

function markMaps() {
  for (var name in mapData) {
    markPlayed(name, mapData[name]["played"]);
    markVetoed(name, mapData[name]["vetoed"]);
  }
}

function markPlayed(map, played) {
  try {
    mapData[map]["played"] = played;
  } catch (e) {
    console.log(e);
    return;
  }
  storeData("mapdata");
  var ul_maplist = document.getElementById("map-list");
  var existing_maps = ul_maplist.getElementsByTagName("li");
  for (var i = 0; i < existing_maps.length; i++) {
    mapElement = existing_maps[i];
    if (mapElement.getElementsByTagName("div")[0].innerHTML.toLowerCase() === map.toLowerCase()) {
      if (played) {
        mapElement.getElementsByTagName("div")[0].classList.add("played");
      } else {
        mapElement.getElementsByTagName("div")[0].classList.remove("played");
      }
      return
    }
  }
}

function markVetoed(map, vetoed) {
  try {
    mapData[map]["vetoed"] = vetoed;
  } catch (e) {
    console.log(e);
    return;
  }
  storeData("mapdata");
  var ul_maplist = document.getElementById("map-list");
  var existing_maps = ul_maplist.getElementsByTagName("li");
  for (var i = 0; i < existing_maps.length; i++) {
    mapElement = existing_maps[i];
    if (mapElement.getElementsByTagName("div")[0].innerHTML.toLowerCase() === map.toLowerCase()) {
      if (vetoed) {
        mapElement.getElementsByTagName("div")[0].classList.add("vetoed");
      } else {
        mapElement.getElementsByTagName("div")[0].classList.remove("vetoed");
      }
      return
    }
  }
}


function addMap(name, played, vetoed) {
  var ul_maplist = document.getElementById("map-list");
  var existing_maps = ul_maplist.getElementsByTagName("li");
  for (var i = 0; i < existing_maps.length; i++) {
    mapElement = existing_maps[i];
    if (mapElement.getElementsByTagName("div")[0].innerHTML.toLowerCase() === name.toLowerCase()) {
      if (played) {
        mapElement.getElementsByTagName("div")[0].classList.add("played");
      } else {
        mapElement.getElementsByTagName("div")[0].classList.remove("played");
      }
      if (vetoed) {
        mapElement.getElementsByTagName("div")[0].classList.add("vetoed");
      } else {
        mapElement.getElementsByTagName("div")[0].classList.remove("vetoed");
      }
      return
    }
  }

  var li = document.createElement("li");
  li.onclick = function() {
    selectMap(name, false)
  };
  var div = document.createElement("div")
  div.innerHTML = name;
  if (played) {
    div.classList.add("played");
  }
  if (vetoed) {
    div.classList.add("vetoed");
  }
  li.appendChild(div);
  ul_maplist.appendChild(li);
}

function removeMaps() {
  var ul_maplist = document.getElementById("map-list");
  var existing_maps = [].slice.call(ul_maplist.getElementsByTagName("li"));
  for (var i = 0; i < existing_maps.length; i++) {
    mapElement = existing_maps[i];
    name = mapElement.getElementsByTagName("div")[0].innerHTML;
    if (!Object.keys(mapData).includes(name)) {
      ul_maplist.removeChild(mapElement);
    }

  }
}

function selectMap(name, alreadyplayed = false, vetoed = false) {
  console.log("selectMap:", name);
  if (!tweenShowMap.isActive()) {
    var maps = document.getElementById("map-list").getElementsByTagName("li");
    for (var i = 0; i < maps.length; i++) {
      mapElement = maps[i];
      if (mapElement.getElementsByTagName("div")[0].innerHTML.toLowerCase() === name.toLowerCase()) {
        if (alreadyplayed) {
          mapElement.getElementsByTagName("div")[0].classList.add("played");
        }
        if (vetoed) {
          mapElement.getElementsByTagName("div")[0].classList.add("vetoed");
        }
        animateInOut(mapElement, name);
        currentMap = name;
        storeData("currentmap");
      } else {
        maps[i].classList.remove("selected");
      }
    }
  }
}

function _selectMap(name) {
  setMapImage(name);
  setMapData(mapData[name]);
}

function setMapImage(name) {
  document.getElementById("map-img").src = mapData[name]["image"].src;
}

function removeMap(name) {
  var maps = document.getElementById("map-list").getElementsByTagName("li");
  for (var i = 0; i < maps.length; i++) {
    if (maps[i].getElementsByTagName("div")[0].innerHTML.toLowerCase() === name.toLowerCase()) {
      document.getElementById("map-list").removeChild(maps[i])
      break;
    }
  }
}

function setMapData(data) {
  for (var key in data) {
    try {
      document.getElementById(key).innerHTML = data[key];
    } catch (e) {}
  }
}

function setPoolName(name) {
  document.getElementById("map-pool").innerHTML = name;
}

function initHide() {
  var box = document.getElementById("map-stats");
  var map = document.getElementById("img-container");
  var left = document.getElementById("left-column");
  var right = document.getElementById("right-column");
  var mapname = document.getElementById("map-name");
  var element1 = document.getElementById("column-content");
  var element2 = document.getElementById("column-bottom");
  var mappool = document.getElementById("map-pool");
  var maplist = document.getElementById("map-list");
  var maps = document.getElementById("map-list").getElementsByTagName("li");
  tweenInitial.staggerTo([left, right, map, mapname, element1, element2, mappool, maplist], 0, {
    opacity: "0"
  }, 0);
  box.style.setProperty("visibility", "visible");
  setPoolName("Map Pool");
  initNeeded = true;
}

function initAnimation(init_map, select = true) {
  if (!tweenInitial.isActive() && initNeeded) {
    console.log("init");
    tweenInitial = new TimelineMax();
    var maplist = document.getElementById("map-list");
    var left = document.getElementById("left-column");
    var right = document.getElementById("right-column");
    var maps = document.getElementById("map-list").getElementsByTagName("li");
    var mappool = document.getElementById("map-pool");
    if (select) setTimeout(selectMap, 500, init_map);
    tweenInitial.delay(0.5)
      .set(left, {
        clearProps: "all"
      })
      .set(right, {
        clearProps: "all"
      })
      .staggerTo([left, right, maplist, mappool], 0, {
        opacity: "1"
      }, 0)
      .to(mappool, 0, {
        x: "+=110%"
      }, 0)
      .staggerTo(maps, 0, {
        x: "+=110%"
      }, 0)
      .staggerFrom([left, right], 0.3, {
        scaleX: 0.0
      }, 0.0)
      .to(mappool, 0.3, {
        x: "-=110%"
      })
      .staggerTo(maps, 0.3, {
        x: "-=110%"
      }, 0.05, "-=0.2")
    initNeeded = false;
  }
}

function outroAnimation() {
  if (!tweenInitial.isActive() && tweenInitial.progress() === 1) {
    initNeeded = true;
    //setTimeout(selectMap, 100, getCurrentMap());
    tweenInitial.eventCallback("onReverseComplete", editMapList);
    tweenInitial.delay(0);
    tweenInitial.reverse(0);
  }
}

function editMapList() {
  addMaps();
  initAnimation(getCurrentMap());
}

function animateInOut(mapElement, name) {
  if (!tweenShowMap.isActive()) {
    //tweenShowMap.clear();
    var args = Array.prototype.slice.call(arguments, 2);

    if (tweenShowMap.progress() === 1) {
      tweenShowMap.eventCallback("onReverseComplete", selectMapAnimation, [name, mapElement, 0.3]);
      tweenShowMap.delay(0);
      tweenShowMap.reverse(0);
    } else {
      var map = document.getElementById("map-img");
      var container = document.getElementById("img-container");
      var mapname = document.getElementById("map-name");
      var element1 = document.getElementById("column-content");
      var element2 = document.getElementById("column-bottom");
      var element1s = Array.prototype.slice.call(document.getElementById("column-content").getElementsByClassName("stat"));
      var element2s = Array.prototype.slice.call(document.getElementById("column-bottom").getElementsByTagName("div"));
      var liquipedia = document.getElementById("liquipedia");
      var mappool = document.getElementById("map-pool");
      tweenShowMap.clear();
      tweenShowMap.staggerTo([container, mapname, element1, element2], 0, {
          opacity: "1"
        }, 0)
        .from(container, 0.4, {
          y: "+=120%",
          ease: Power1.easeOut
        })
        .staggerFrom([mapname, liquipedia].concat(element1s, element2s), 0.3, {
          x: "-=110%"
        }, 0.05, "-=0.2")
        .set(map, {
          clearProps: "all"
        });
      selectMapAnimation(name, mapElement, 0.2);
    }
  }
}

function selectMapAnimation(name, mapElement, delay) {
  _selectMap(name);
  tweenShowMap.delay(delay);
  tweenShowMap.restart(true);
  var tween = new TimelineMax();
  tween.delay(delay)
    .to(mapElement, 0, {
      className: "+=selected"
    }, "+=0.2")
    .to(mapElement, 0, {
      className: "-=selected"
    }, "+=0.3")
    .to(mapElement, 0, {
      className: "+=selected"
    }, "+=0.4");
}

function setColors(color1, color2) {
  if (color1 != null) {
    document.documentElement.style.setProperty("--color", color1);
    colors["color1"] = color1;
  }
  if (color2 != null) {
    document.documentElement.style.setProperty("--color2", color2);
    colors["color2"] = color2;
  }
  storeData("colors");
}
