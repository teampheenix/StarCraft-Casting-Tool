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

window.onload = function() {
        init();
}

function init() {
        initHide();
        connectWebsocket();
        myDefaultFont = getComputedStyle(document.body).getPropertyValue('--font');
        setPoolName("Map Pool");
}


function connectWebsocket() {
	console.time('connectWebsocket');
        socket = new WebSocket("ws://127.0.0.1:4489/mapstats");

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
                        data = jsonObject.data;
                        addMaps(data);
                        initAnimation(Object.keys(data)[0]);
                } else if (jsonObject.event == 'SELECT_MAP') {
                        selectMap(jsonObject.data.map)
                }
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

function addMaps(data) {
        for (var name in data) {
                addMap(name);
                data[name]['image'] = new Image();
                data[name]['image'].src = 'src/img/maps/'.concat(name.replace(/\s/g, "_"), '.jpg');
        }
}

function addMap(name) {
        var ul_maplist = document.getElementById('map-list');
        var li = document.createElement("li");
        li.onclick = function() {
                selectMap(name, 0.5)
        };
        var div = document.createElement("div")
        div.innerHTML = name;
        li.appendChild(div);
        ul_maplist.appendChild(li);
}

function selectMap(name) {
        var maps = document.getElementById('map-list').getElementsByTagName("li");
        for (var i = 0; i < maps.length; i++) {
                mapElement = maps[i];
                if (mapElement.getElementsByTagName('div')[0].innerHTML.toLowerCase() == name.toLowerCase()) {
                        animateInOut(mapElement, name);
                } else {
                        maps[i].classList.remove('selected');
                }
        }
}

function _selectMap(name) {
        setMapImage(name);
        setMapData(data[name]);
}

function setMapImage(name) {
        document.getElementById('map-img').src = data[name]['image'].src;
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

function initHide(){
        var map = document.getElementById("map-img");
        var mapname = document.getElementById("map-name");
        var element1 = document.getElementById("column-content");
        var element2 = document.getElementById("column-bottom");
        var mappool = document.getElementById("map-pool");
        var maps = document.getElementById('map-list').getElementsByTagName("li");
        tweenInitial.staggerTo([map, mapname, element1, element2, mappool], 0, {
                        opacity: "0"
                }, 0);
        initNeeded = true;
}

function initAnimation(init_map) {
        if(initNeeded){
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
        if (!tweenShowMap.isActive()){
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
        document.documentElement.style.setProperty('--color', color1);
        document.documentElement.style.setProperty('--color2', color2);
}


function setFont(font) {
        if (font == 'DEFAULT') {
                font = myDefaultFont;
        }
        document.documentElement.style.setProperty('--font', font);
}

function changeCSS(cssFile, cssLinkIndex) {
        var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);

        var newlink = document.createElement("link");
        newlink.setAttribute("rel", "stylesheet");
        newlink.setAttribute("type", "text/css");
        newlink.setAttribute("href", cssFile);

        document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
}
