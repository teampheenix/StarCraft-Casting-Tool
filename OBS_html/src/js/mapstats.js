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
var storage = window.localStorage;

var mapData = {};
var colors = {};
var font = "DEFAULT";
var currentMap = "";

window.onload = function() {
        init();
}

function init() {
        myDefaultFont = getComputedStyle(document.body).getPropertyValue('--font');
        loadStoredData();
        initHide();
        connectWebsocket();
        if (Object.keys(mapData).length > 0) initAnimation(getCurrentMap());
}

function getCurrentMap() {
        if (currentMap == "" || currentMap == undefined || !Object.keys(mapData).includes(currentMap)) {
                try {
                        currentMap = Object.keys(mapData)[0];
                } catch {
                        currentMap = "";
                }

        }
        if (currentMap == undefined) currentMap = "";
        return currentMap;

}

function storeData(scope = null) {
        if (scope == null || scope == "mapdata") storage.setItem('scct-mapstats-mapdata', JSON.stringify(mapData));
        if (scope == null || scope == "colors") storage.setItem('scct-mapstats-colors', JSON.stringify(colors));
        if (scope == null || scope == "font") storage.setItem('scct-mapstats-font', font);
        if (scope == null || scope == "currentmap") storage.setItem('scct-mapstats-currentmap', currentMap);
}

function loadStoredData() {
        mapData = JSON.parse(storage.getItem('scct-mapstats-mapdata'));
        colors = JSON.parse(storage.getItem('scct-mapstats-colors'));
        font = storage.getItem('scct-mapstats-font');
        currentMap = storage.getItem('scct-mapstats-currentmap');
        if (currentMap == null) currentMap = "";
        if (colors == null) colors = {};
        if (mapData == null) mapData = {};
        try {
                setColors(colors['color1'], colors['color2']);
        } catch {}
        try {
                setFont(font);
        } catch {}
        loadImages();
        addMaps();
}

function connectWebsocket() {
        console.time('connectWebsocket');
        path = "mapstats"
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
                        changeCSS(jsonObject.data.file, 0);
                } else if (jsonObject.event == 'CHANGE_COLORS') {
                        setColors(jsonObject.data.color1, jsonObject.data.color2);
                } else if (jsonObject.event == 'CHANGE_FONT') {
                        setFont(jsonObject.data.font);
                } else if (jsonObject.event == 'MAPSTATS') {
                        var doInit = Object.keys(mapData).length == 0;
                        mapData = jsonObject.data;
                        loadImages();
                        storeData("mapdata");
                        outroAnimation();
                        if (doInit) initAnimation(getCurrentMap());
                } else if (jsonObject.event == 'SELECT_MAP') {
                        selectMap(jsonObject.data.map)
                } else if (jsonObject.event == 'DEBUG_MODE') {}
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

function loadImages() {
        for (var name in mapData) {
                mapData[name]['image'] = new Image();
                mapData[name]['image'].src = 'src/img/maps/'.concat(name.replace(/\s/g, "_"), '.jpg');
        }
}

function addMaps(){
        removeMaps();
        for (var name in mapData) {
                addMap(name);
        }
}

function addMap(name) {
        var ul_maplist = document.getElementById('map-list');
        var existing_maps = ul_maplist.getElementsByTagName("li");
        for (var i = 0; i < existing_maps.length; i++) {
                mapElement = existing_maps[i];
                if (mapElement.getElementsByTagName('div')[0].innerHTML.toLowerCase() == name.toLowerCase()) {
                        return
                }
        }

        var li = document.createElement("li");
        li.onclick = function() {
                selectMap(name, 0.5)
        };
        var div = document.createElement("div")
        div.innerHTML = name;
        li.appendChild(div);
        ul_maplist.appendChild(li);
}

function removeMaps() {
        var ul_maplist = document.getElementById('map-list');
        var existing_maps = ul_maplist.getElementsByTagName("li");
        for (var i = 0; i < existing_maps.length; i++) {
                mapElement = existing_maps[i];
                name = mapElement.getElementsByTagName('div')[0].innerHTML;
                if(!Object.keys(mapData).includes(name)){
                        ul_maplist.removeChild(mapElement);
                }

        }
}

function selectMap(name) {
        var maps = document.getElementById('map-list').getElementsByTagName("li");
        for (var i = 0; i < maps.length; i++) {
                mapElement = maps[i];
                if (mapElement.getElementsByTagName('div')[0].innerHTML.toLowerCase() == name.toLowerCase()) {
                        animateInOut(mapElement, name);
                        currentMap = name;
                        storeData('currentmap');
                } else {
                        maps[i].classList.remove('selected');
                }
        }
}

function _selectMap(name) {
        setMapImage(name);
        setMapData(mapData[name]);
}

function setMapImage(name) {
        document.getElementById('map-img').src = mapData[name]['image'].src;
}

function removeMap(name) {
        var maps = document.getElementById('map-list').getElementsByTagName("li");
        for (var i = 0; i < maps.length; i++) {
                if (maps[i].getElementsByTagName('div')[0].innerHTML.toLowerCase() == name.toLowerCase()) {
                        document.getElementById('map-list').removeChild(maps[i])
                        break;
                }
        }
}

function setMapData(data) {
        for (var key in data) {
                try {
                        document.getElementById(key).innerHTML = data[key];
                } catch (err) {}
        }
}

function setPoolName(name) {
        document.getElementById('map-pool').innerHTML = name;
}

function initHide() {
        var box = document.getElementById("map-stats");
        var map = document.getElementById("map-img");
        var mapname = document.getElementById("map-name");
        var element1 = document.getElementById("column-content");
        var element2 = document.getElementById("column-bottom");
        var mappool = document.getElementById("map-pool");
        var maps = document.getElementById('map-list').getElementsByTagName("li");
        tweenInitial.staggerTo([map, mapname, element1, element2, mappool], 0, {
                opacity: "0"
        }, 0);
        box.style.setProperty('visibility', 'visible');
        setPoolName("Map Pool");
        initNeeded = true;
}

function initAnimation(init_map) {
        if (!tweenInitial.isActive() && initNeeded) {
                tweenInitial.clear();
                var map = document.getElementById("map-img");
                var mapname = document.getElementById("map-name");
                var element1 = document.getElementById("column-content");
                var element2 = document.getElementById("column-bottom");
                var mappool = document.getElementById("map-pool");
                var maps = document.getElementById('map-list').getElementsByTagName("li");
                tweenInitial.delay(0.5)
                        .staggerTo([map, mapname, element1, element2], 0, {
                                opacity: "0"
                        }, 0)
                        .call(selectMap, [init_map])
                        .to(mappool, 0, {
                                opacity: "1"
                        }, 0)
                        .from(mappool, 0.3, {
                                x: '+=110%'
                        })
                        .staggerFrom(maps, 0.3, {
                                x: '+=110%'
                        }, 0.05, '-=0.2')
                initNeeded = false;
        }
}

function animateInOut(mapElement, name) {
        if (!tweenShowMap.isActive()) {
                //tweenShowMap.clear();
                var args = Array.prototype.slice.call(arguments, 2);

                if (tweenShowMap.progress() == 1) {
                        tweenShowMap.eventCallback("onReverseComplete", selectMapAnimation, [name, mapElement, 0.3]);
                        tweenShowMap.delay(0);
                        tweenShowMap.reverse(0);
                } else {
                        var map = document.getElementById("map-img");
                        var mapname = document.getElementById("map-name");
                        var element1 = document.getElementById("column-content");
                        var element2 = document.getElementById("column-bottom");
                        var element1s = Array.prototype.slice.call(document.getElementById('column-content').getElementsByClassName("stat"));
                        var element2s = Array.prototype.slice.call(document.getElementById('column-bottom').getElementsByTagName("div"));
                        var mappool = document.getElementById("map-pool");
                        tweenShowMap.clear();
                        tweenShowMap.staggerTo([map, mapname, element1, element2], 0, {
                                        opacity: "1"
                                }, 0)
                                .from(map, 0.4, {
                                        bottom: '-=100%',
                                        ease: Power1.easeOut
                                })
                                .staggerFrom([mapname].concat(element1s, element2s), 0.3, {
                                        x: '-=110%'
                                }, 0.05, '-=0.2');
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
                }, '+=0.2')
                .to(mapElement, 0, {
                        className: "-=selected"
                }, '+=0.3')
                .to(mapElement, 0, {
                        className: "+=selected"
                }, '+=0.4');
}

function setColors(color1, color2) {
        if (color1 != null) {
                document.documentElement.style.setProperty('--color', color1);
                colors["color1"] = color1;
        }
        if (color2 != null) {
                document.documentElement.style.setProperty('--color2', color2);
                colors["color2"] = color2;
        }
        storeData("colors");
}


function setFont(newFont) {
        if (newFont == 'DEFAULT') {
                newFont = myDefaultFont;
        }
        font = newFont.trim();
        document.documentElement.style.setProperty('--font', font);
        storeData("font");
}

function changeCSS(cssFile, cssLinkIndex) {
        var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);

        var newlink = document.createElement("link");
        newlink.setAttribute("rel", "stylesheet");
        newlink.setAttribute("type", "text/css");
        newlink.setAttribute("href", cssFile);

        document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
}
