var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var volume = 1.0;
var debug = false;
var displayTime = 3.0;
var tween = new TimelineMax()
var myAudio1 = new Audio("src/sound/flyin.wav");
myAudio1.volume = volume;
var myAudio2 = new Audio("src/sound/bass.wav");
myAudio2.volume = volume;
var myAudio3 = new Audio("src/sound/fanfare.wav");
myAudio3.volume = volume;

window.onload = function() {
        init();
}

function playSound1() {
        myAudio1.play();
}

function playSound2() {
        myAudio2.play();
}

function playSound3() {
        myAudio3.play();
}

function Connect() {
        path = "intro"
        port = parseInt("0x".concat(profile), 16);
        socket = new WebSocket("ws://127.0.0.1:".concat(port, "/", path));

        socket.onopen = function() {
                console.log("Connected!");
                isopen = true;
        }

        socket.onmessage = function(message) {
                var jsonObject = JSON.parse(message.data);
                var intro = document.getElementById("intro");
                if (jsonObject.data.hasOwnProperty('font')) {
                        intro.style.fontFamily = jsonObject.data.font;
                }
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
                                var racelogo = document.getElementsByClassName("race")[0];
                                var offset = (window.innerWidth - intro.offsetWidth) / 2;
                                var introWidth = intro.clientWidth;
                                var introHeight = intro.clientHeight;
                                var racelogoWidth = racelogo.clientWidth;
                                var racelogoHeight = racelogo.clientHeight;
                                var logoTransHeight = racelogoHeight;
                                var logoTransWidth = racelogoWidth;
                                if ((racelogoHeight - introHeight) > 0) {
                                        logoTransHeight = 0;
                                        logoTransWidth = 0;
                                };
                                myAudio1.volume = jsonObject.data.volume / 10.0;
                                myAudio2.volume = jsonObject.data.volume / 10.0;
                                myAudio3.volume = jsonObject.data.volume / 10.0;
                                var animation = "default";
                                if (jsonObject.data.hasOwnProperty('animation')) {
                                        animation = jsonObject.data.animation;
                                } else {
                                        animation = "default";
                                }
                                if (animation == "fanfare") {
                                        tween.call(playSound3)
                                                .to(intro, 0, {
                                                        opacity: 0,
                                                        left: offset + "px",
                                                        height: "0px"
                                                })
                                                .to(racelogo, 0, {
                                                        height: logoTransHeight + "px"
                                                })
                                                .to(intro, 0.1, {
                                                        opacity: 1,
                                                        height: "0px"
                                                })
                                                .to(intro, 0.35, {
                                                        ease: Power2.easeOut,
                                                        height: introHeight + "px"
                                                })
                                                .to(racelogo, 0.35, {
                                                        ease: Power2.easeOut,
                                                        height: racelogoHeight + "px"
                                                }, "-=0.35")
                                                .to(intro, jsonObject.data.display_time, {
                                                        height: introHeight + "px"
                                                })
                                                .to(intro, 0.35, {
                                                        height: "0px",
                                                        ease: Power1.easeOut
                                                })
                                                .to(racelogo, 0.35, {
                                                        ease: Power2.easeOut,
                                                        height: logoTransHeight + "px"
                                                }, "-=0.35")
                                                .to(intro, 0, {
                                                        left: "105%",
                                                        opacity: 0,
                                                        height: ""
                                                })
                                                .to(racelogo, 0, {
                                                        height: ""
                                                });
                                } else if (animation == "slide") {
                                        tween.to(intro, 0, {
                                                        opacity: 0,
                                                        left: offset + introWidth / 2 + "px",
                                                        width: "0px"
                                                })
                                                .to(racelogo, 0, {
                                                        width: logoTransWidth + "px"
                                                })
                                                .to(intro, 0.1, {
                                                        opacity: 1,
                                                        left: offset + introWidth / 2 + "px",
                                                })
                                                .call(playSound2)
                                                .to(intro, 0.35, {
                                                        ease: Power2.easeOut,
                                                        width: introWidth + "px",
                                                        left: offset + "px"
                                                })
                                                .to(racelogo, 0.35, {
                                                        ease: Power2.easeOut,
                                                        width: racelogoWidth + "px"
                                                }, "-=0.35")
                                                .to(intro, jsonObject.data.display_time, {
                                                        width: introWidth + "px"
                                                })
                                                .call(playSound2)
                                                .to(intro, 0.35, {
                                                        left: offset + introWidth / 2 + "px",
                                                        width: "0px",
                                                        ease: Power2.easeIn
                                                })
                                                .to(racelogo, 0.35, {
                                                        ease: Power2.easeIn,
                                                        width: logoTransWidth + "px"
                                                }, "-=0.35")
                                                .to(intro, 0, {
                                                        left: "105%",
                                                        opacity: 0,
                                                        width: ""
                                                })
                                                .to(racelogo, 0, {
                                                        width: ""
                                                });
                                } else {
                                        tween.call(playSound1)
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
                        }

                } else if (jsonObject.event == 'CHANGE_STYLE') {
                        changeCSS(jsonObject.data.file, 0);
                        fillText();
                } else if (jsonObject.event == 'DEBUG_MODE') {
                        if (!debug) {
                                tween.kill()
                                var offset = (window.innerWidth - intro.offsetWidth) / 2;
                                TweenLite.to(intro, 0, {
                                        opacity: 1,
                                        left: offset + "px"
                                });
                                debug = true;
                        } else {
                                tween.kill()
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

function fillText() {
        $("div.box").find(".text-fill").textfill({
                maxFontPixels: 60
        });
}

function changeCSS(newCssFile, cssLinkIndex) {
        var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);
        var newlink = document.createElement("link");
        newlink.setAttribute("rel", "stylesheet");
        newlink.setAttribute("type", "text/css");
        newlink.setAttribute("href", newCssFile);
        if(newCssFile!="null"){
                if (oldlink.href != newlink.href){
                        document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
                }
        }

}


function init() {
        var intro = document.getElementById("intro");
        TweenLite.to(intro, 0, {
                opacity: 1,
                left: "105%"
        });
        intro.style.setProperty('visibility', 'visible');
        Connect();
}
