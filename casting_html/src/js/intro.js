var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var volume = 1.0;
var debug = false;
var displayTime = 3.0;
var cssFile = "";
var tween = new TimelineMax()
var myAudio1 = new Audio("src/sound/flyin.wav");
myAudio1.volume = volume;
var myAudio2 = new Audio("src/sound/bass.wav");
myAudio2.volume = volume;
var myAudio3 = new Audio("src/sound/fanfare.wav");
myAudio3.volume = volume;
var controller = new Controller(profile, 'intro');

init();

function playSound(audio) {
  try {
    if (audio.duration > 0 && !audio.paused) {
      //already playing
      audio.pause();
      audio.currentTime = 0;
      audio.play();
    } else {
      //not playing
      audio.play();
    }
  } catch (e) {}
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
        try {
          var tts = new Audio(jsonObject.data.tts);
          tts.volume = jsonObject.data.tts_volume / 20.0;
        } catch (e) {}
        socket.send(jsonObject.state);
        tween.clear();
        $(".race").prop('id', jsonObject.data.race);
        $(".logo").css("display", jsonObject.data.display)
        $(".logo").css("background-image", "url(" + jsonObject.data.logo + ")");
        $('.name span').html(jsonObject.data.name);
        $('.team span').html(jsonObject.data.team);
        fillText();
        var racelogo = document.getElementsByClassName("race")[0];
        var offset = (window.innerWidth - intro.offsetWidth) / 2;
        myAudio1.volume = jsonObject.data.volume / 40.0;
        myAudio2.volume = jsonObject.data.volume / 40.0;
        myAudio3.volume = jsonObject.data.volume / 40.0;
        var animation = "default";
        if (jsonObject.data.hasOwnProperty('animation')) {
          animation = jsonObject.data.animation;
        } else {
          animation = "default";
        }
        if (animation == "fanfare") {
          tween.call(playSound, [myAudio3])
            .to(intro, 0, {
              opacity: 0,
              clearProps: 'left',
              transformOrigin: "right top",
              scaleY: 0
            })
            .to(intro, 0.1, {
              opacity: 1,
            })
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
            .to(intro, 0, {
              left: "105%",
              clearProps: "transform, transformOrigin",
              opacity: 0
            });
        } else if (animation == "slide") {
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
            .call(playSound, [tts])
            .to(intro, jsonObject.data.display_time, {
              left: offset + "px"
            })
            .to(intro, 0.5, {
              opacity: 0,
              ease: Power1.easeInOut
            })
            .to(intro, 0, {
              left: "105%",
              opacity: 0
            });
        }
      }

    } else if (jsonObject.event == 'CHANGE_STYLE') {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event == 'DEBUG_MODE') {
      if (!debug) {
        tween.kill()
        var offset = (window.innerWidth - intro.offsetWidth) / 2;
        $('#intro').css('opacity', '1');
        $('#intro').css('left', offset.toString() + "px");
        debug = true;
      } else {
        tween.kill()
        $('#intro').css('opacity', '0');
        $('#intro').css('left', '105%');
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

function init() {
  var intro = document.getElementById("intro");
  $('#intro').css('visibility', 'visible');
  $('#intro').css('left', '105%');
  Connect();
}
