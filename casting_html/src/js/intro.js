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
var controller = new Controller(profile, "intro");

init();

function playSound(audio) {
  try {
    if (!!audio) {
      if (audio.duration > 0 && !audio.paused) {
        //already playing
        audio.pause();
        audio.currentTime = 0;
        audio.play();
      } else {
        //not playing
        audio.play();
      }
    }
  } catch (e) { }
}

function connect() {
  try {
    socket = new WebSocket(controller.generateKeyURI());
  } catch (e) { }

  socket.onopen = function () {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function (message) {
    var jsonObject = JSON.parse(message.data);
    var intro = document.getElementById("intro");
    var asset1 = document.getElementById("asset1");
    var asset2 = document.getElementById("asset2");
    if (jsonObject.data.hasOwnProperty("font")) {
      intro.style.fontFamily = jsonObject.data.font;
    }
    console.log("Message received");
    if (jsonObject.event === "SHOW_INTRO") {
      if (!tween.isActive()) {
        try {
          var tts = new Audio(jsonObject.data.tts);
          tts.volume = jsonObject.data.tts_volume / 20.0;
        } catch (e) { }
        socket.send(jsonObject.state);
        tween.clear();
        const cssItems = [".box", ".race", ".logo", ".name", ".team", ".misc", ".label", ".label2", ".label3", ".asset1", ".asset2"];
        $(".race").prop("id", jsonObject.data.race);
        $(".logo").css("display", jsonObject.data.display)
        $(".logo").css("background-image", "url(" + jsonObject.data.logo + ")");
        $(".name span").html(jsonObject.data.name);
        $(".team span").html(jsonObject.data.team);
        if (jsonObject.data.default_logo) {
          cssItems.forEach((element) => {
            $(element).addClass("defaultLogo");
          });
        } else {
          cssItems.forEach((element) => {
            $(element).removeClass("defaultLogo");
          });
        }
        fillText();
        var racelogo = document.getElementsByClassName("race")[0];
        var offset = (window.innerWidth - intro.offsetWidth) / 2;
        myAudio1.volume = jsonObject.data.volume / 40.0;
        myAudio2.volume = jsonObject.data.volume / 40.0;
        myAudio3.volume = jsonObject.data.volume / 40.0;
        var animation = "default";
        if (jsonObject.data.hasOwnProperty("animation")) {
          animation = jsonObject.data.animation;
        } else {
          animation = "default";
        }
        if (animation === "fanfare") {
          tween.call(playSound, [myAudio3])
            .to(intro, 0, {
              opacity: 0,
              clearProps: "left",
              transformOrigin: "right top",
              scaleY: 0
            })
            .to(intro, 0.1, {
              opacity: 1,
            })
            .staggerTo([asset1, asset2], 0.35, {
              ease: Power2.easeIn,
              opacity: 1
            }, 0.0, "=-0.35")
            .to(intro, 0.35, {
              ease: Power2.easeOut,
              scaleY: 1
            })
            .call(playSound, [tts])
            .to(intro, jsonObject.data.display_time, {
              scaleY: 1
            })
            .to(intro, 0.35, {
              scaleY: 0,
              ease: Power1.easeOut
            })
            .staggerTo([asset1, asset2], 0.50, {
              ease: Power2.easeOut,
              opacity: 0
            }, 0.0, "=-0.35")
            .to(intro, 0, {
              left: "105%",
              clearProps: "transform, transformOrigin",
              opacity: 0
            });
        } else if (animation === "slide") {
          tween.to(intro, 0, {
            opacity: 0,
            left: offset + "px",
            scaleX: 0
          })
            .to(intro, 0.1, {
              opacity: 1
            })
            .call(playSound, [myAudio2])
            .to(intro, 0.35, {
              ease: Power2.easeOut,
              scaleX: 1,
              force3D: true
            })
            .staggerTo([asset1, asset2], 0.35, {
              ease: Power2.easeIn,
              opacity: 1
            }, 0.0, "=-0.4")
            .call(playSound, [tts])
            .to(intro, jsonObject.data.display_time, {
              scaleX: 1
            })
            .call(playSound, [myAudio2])
            .to(intro, 0.35, {
              scaleX: 0,
              force3D: true,
              ease: Power2.easeIn
            })
            .staggerTo([asset1, asset2], 0.35, {
              ease: Power2.easeIn,
              opacity: 0
            }, 0.0, "=-0.4")
            .to(intro, 0, {
              left: "105%",
              opacity: 0,
              clearProps: "transform"
            });
        } else {
          tween.call(playSound, [myAudio1])
            .to(intro, 0, {
              opacity: 1,
              left: "105%"
            })
            .to(intro, 1.12, {
              ease: Power2.easeIn,
              left: offset + "px"
            })
            .staggerTo([asset1, asset2], 0.2, {
              ease: Power2.easeIn,
              opacity: 1
            }, 0.0, "=-0.2")
            .call(playSound, [tts])
            .to(intro, jsonObject.data.display_time, {
              left: offset + "px"
            })
            .to(intro, 0.5, {
              opacity: 0,
              ease: Power1.easeInOut
            })
            .staggerTo([asset1, asset2], 0.5, {
              ease: Power2.easeInOut,
              opacity: 0
            }, 0.0, "=-0.5")
            .to(intro, 0, {
              left: "105%",
              opacity: 0
            });
        }
      }

    } else if (jsonObject.event === "CHANGE_STYLE") {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event === "DEBUG_MODE") {
      if (!debug) {
        tween.kill()
        var offset = (window.innerWidth - intro.offsetWidth) / 2;
        $("#intro").css("opacity", "1");
        $("#asset1").css("opacity", "1");
        $("#asset2").css("opacity", "1");
        $("#intro").css("left", offset.toString() + "px");
        debug = true;
      } else {
        tween.kill()
        $("#intro").css("opacity", "0");
        $("#asset1").css("opacity", "0");
        $("#asset2").css("opacity", "0");
        $("#intro").css("left", "105%");
        debug = false;
      }

    }
  }

  socket.onclose = function (e) {
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function () {
      connect();
    }, reconnectIntervalMs);
  }
}

function fillText() {
  $("div.box").find(".text-fill").textfill({
    maxFontPixels: 60
  });
}

function init() {
  var intro = document.getElementById("intro");
  $("#intro").css("visibility", "visible");
  $("#asset1").css("visibility", "visible");
  $("#asset2").css("visibility", "visible");
  $("#asset1").css("opacity", "0");
  $("#asset2").css("opacity", "0");
  $("#intro").css("left", "105%");
  connect();
}