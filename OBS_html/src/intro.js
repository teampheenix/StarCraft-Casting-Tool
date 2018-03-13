var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var volume = 1.0;
var debug = false;
var displayTime = 3.0;
var tween = new TimelineMax()
var myAudio = new Audio("src/sound.wav");
myAudio.volume = volume;

function Connect() {

        socket = new WebSocket("ws://127.0.0.1:4489/intro");

        socket.onopen = function() {
                console.log("Connected!");
                isopen = true;
        }

        socket.onmessage = function(message) {
                var jsonObject = JSON.parse(message.data);
                console.log("Message received");
                if (jsonObject.event == 'SHOW_INTRO') {
                        if (!tween.isActive()) {
                                tween.clear();
                                $(".race").prop('id', jsonObject.data.race);
                                $(".logo").css("display", jsonObject.data.display)
                                $(".logo").css("background-image", "url(" + jsonObject.data.logo + ")");
                                $('.name span').html(jsonObject.data.name);
                                $('.team span').html(jsonObject.data.team);
                                fillText();
                                var intro = document.getElementById("intro");
                                var offset = (window.innerWidth - intro.offsetWidth) / 2;
                                myAudio.volume = jsonObject.data.volume / 10.0;
                                tween.call(playSound)
                                        .to(intro, 0, {
                                                opacity: 1,
                                                left: "105%"
                                        })
                                        .to(intro, 1.12, {
                                                ease: Power2.easeIn,
                                                left: offset + "px"
                                        })
                                        .to(intro, jsonObject.data.display_time, {
                                                left: offset + "px"
                                        })
                                        .to(intro, 0.5, {
                                                opacity: 0,
                                                ease: Power1.easeInOut
                                        })
                                        .to(intro, 0, {
                                                left: "105%"
                                        });
                        }

                } else if (jsonObject.event == 'CHANGE_STYLE') {
                        changeCSS(jsonObject.data.file, 0);
                        fillText();
                } else if (jsonObject.event == 'DEBUG_MODE') {
                        if(!debug){
                                tween.kill()
                                var intro = document.getElementById("intro");
                                var offset = (window.innerWidth - intro.offsetWidth) / 2;
                                TweenLite.to(intro, 0, {
                                        opacity: 1,
                                        left: offset + "px"
                                });
                                debug = true;
                        }else{
                                tween.kill()
                                var intro = document.getElementById("intro");
                                TweenLite.to(intro, 0, {
                                        opacity: 0
                                });
                                debug = false;
                        }

                }
        }

        socket.onclose = function(e) {
                console.log("Connection closed.");
                socket = null;
                isopen = false
                setTimeout(function() {
                        Connect();
                }, reconnectIntervalMs);
        }
};

function playSound() {
        myAudio.play();
}

function sendText() {
        if (isopen) {
                socket.send("Hello, world!");
                console.log("Text message sent.");
        } else {
                console.log("Connection not opened.")
        }
};

function fillText() {
        $("div.box").find(".text-fill").textfill({
                maxFontPixels: 60
        });
}

function changeCSS(cssFile, cssLinkIndex) {
        var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);

        var newlink = document.createElement("link");
        newlink.setAttribute("rel", "stylesheet");
        newlink.setAttribute("type", "text/css");
        newlink.setAttribute("href", cssFile);

        document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
}

var intro = document.getElementById("intro");
TweenLite.to(intro, 0, {
        opacity: 1,
        left: "105%"
});
Connect();
