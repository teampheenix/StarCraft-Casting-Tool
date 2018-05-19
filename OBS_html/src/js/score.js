var tweens = {};
var socket = null;
var isopen = false;
var myDefaultFont = null;
var reconnectIntervalMs = 5000;
var data = {};
var font = "DEFAULT";
var cssFile = "";
var initNeeded = true;
var tweenInitial = new TimelineMax();
var tweens = {};

// data['team1'] = "Team 1";
// data['team2'] = "Team 2";
// data['score1'] = "1";
// data['score2'] = "2";
// data['logo1'] = "data/logos/64f38e.png";
// data['logo2'] = "data/logos/64f38e.png";
// data['sets'] = {};
// data['sets'][1] = {};
// data['sets'][1][1] = 'red';
// data['sets'][1][2] = 'green';
// data['sets'][2] = {};
// data['sets'][2][1] = 'red';
// data['sets'][2][2] = 'green';
// data['sets'][3] = {};
// data['sets'][3][1] = 'red';
// data['sets'][3][2] = 'green';
// data['sets'][4] = {};
// data['sets'][4][1] = 'grey';
// data['sets'][4][2] = 'grey';
// data['sets'][5] = {};
// data['sets'][5][1] = 'grey';
// data['sets'][5][2] = 'grey';
//changeCSS("src/css/score/Alternative.css");
init();

function init() {
        myDefaultFont = getComputedStyle(document.body).getPropertyValue('--font');
        loadStoredData();
        initHide();
        connectWebsocket();
        setTimeout(function() {
                initAnimation(false);
        }, 1000);
        // changeCSS("src/css/score/Alternative.css");
        // setTimeout(function() {
        //         changeText('team1', "team pheeniX");
        // }, 2000);
        // setTimeout(function() {
        //         changeText('team2', "MindGaming");
        // }, 3000);
        // setTimeout(function() {
        //         changeText('score1', "3");
        // }, 4000);
        // setTimeout(function() {
        //         changeText('score2', "4");
        // }, 4500);
        // setTimeout(function() {
        //         changeImage('logo1', "data/logos/679f86.png");
        //         changeScoreIcon(1, 4, 'green')
        //         changeScoreIcon(2, 4, 'red')
        // }, 4000);
        // setTimeout(function() {
        //         outroAnimation();
        // }, 3000);
}

function connectWebsocket() {
        console.time('connectWebsocket');
        path = "score"
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
                        changeCSS(jsonObject.data.file);
                } else if (jsonObject.event == 'CHANGE_FONT') {
                        setFont(jsonObject.data.font);
                } else if (jsonObject.event == 'ALL_DATA') {
                        if (dataChanged(jsonObject.data)) {
                                initAnimation();
                        }
                } else if (jsonObject.event == 'CHANGE_TEXT') {
                        changeText(jsonObject.data.id, jsonObject.data.text);
                } else if (jsonObject.event == 'CHANGE_IMAGE') {
                        changeImage(jsonObject.data.id, jsonObject.data.img);
                } else if (jsonObject.event == 'CHANGE_SCORE') {
                        changeScoreIcon(jsonObject.data.teamid, jsonObject.data.setid, jsonObject.data.color);
                } else if (jsonObject.event == 'SET_WINNER') {
                        setWinner(jsonObject.data);
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
        if (JSON.stringify(data) === JSON.stringify(newData)) {
                return false;
        } else {
                data = newData;
                return true;
        }

}

function storeData(scope = null) {
        try {
                var storage = window.localStorage;
                if (scope == null || scope == "data") storage.setItem('scct-' + profile + '-score-data', JSON.stringify(data));
                if (scope == null || scope == "font") storage.setItem('scct-' + profile + '-score-font', font);
                if (scope == null || scope == "css") storage.setItem('scct-' + profile + '-score-css', cssFile);
        } catch (e) {}
}

function loadStoredData() {
        try {
                var storage = window.localStorage;
                data = JSON.parse(storage.getItem('scct-' + profile + '-score-data'));
                font = storage.getItem('scct-' + profile + '-score-font');
                cssFile = storage.getItem('scct-' + profile + '-score-css');
                if (data == null) data = {};
                try {
                        changeCSS(cssFile);
                } catch (e) {}

                try {
                        setFont(font);
                } catch (e) {}

        } catch (e) {}
}

function insertData() {
        storeData('data');
        $('#team1').text(data['team1']);
        $('#team2').text(data['team2']);
        $('#score1').text(data['score1']);
        $('#score2').text(data['score2']);
        $('#logo1').css("background-image", "url('../" + data['logo1'] + "')");
        $('#logo2').css("background-image", "url('../" + data['logo2'] + "')");
        if (data['winner'][0]) {
                $('#team1').addClass('winner');
        } else {
                $('#team1').removeClass('winner');
        }
        if (data['winner'][1]) {
                $('#team2').addClass('winner');
        } else {
                $('#team2').removeClass('winner');
        }
        insertIcons();
        $(document).ready(function() {
                $('#content').find(".text-fill").textfill();
        });
}

function setWinner(winner) {
        if (winner == 0) {
                $('#team1').removeClass('winner');
                $('#team2').removeClass('winner');
        } else if (winner == 1) {
                $('#team2').addClass('winner');
                $('#team1').removeClass('winner');
        } else if (winner == -1) {
                $('#team1').addClass('winner');
                $('#team2').removeClass('winner');
        }
}

function insertIcons() {
        for (var j = 0; j < 2; j++) {
                $('#score' + (j + 1).toString() + '-box').empty();
        }
        try {
                for (var i = 0; i < Object.keys(data['sets']).length; i++) {
                        for (var j = 0; j < 2; j++) {
                                var color = data['sets'][i][j];
                                $('#score' + (j + 1).toString() + '-box').append('<div class="circle" id="circle-' + (j + 1).toString() + '-' + (i + 1).toString() + '" style="background-color: ' + color + '"></div>');
                        }
                }
        } catch (e) {}
}

function changeCSS(newCssFile) {
        if (newCssFile && newCssFile != "null") {
                cssFile = newCssFile;
                console.log('CSS file changed to', newCssFile);
                $('link[rel="stylesheet"]').attr('href', newCssFile);
                storeData("css");
        }
}

function initHide() {
        var content = document.getElementById("content");
        content.style.setProperty('visibility', 'visible');
        tweenInitial.staggerTo([content], 0, {
                opacity: "0"
        }, 0);
}

function initAnimation(force = true) {
        if (!tweenInitial.isActive() && initNeeded) {
                console.log(1);
                insertData();
                tweenInitial = new TimelineMax();
                tweenInitial.delay(0.5)
                        .fromTo([$('#content')], 0, {
                                opacity: "0"
                        }, {
                                opacity: "1"
                        }, 0)
                        .fromTo($('#box'), 0.35, {
                                scaleY: 0.0,
                                force3D: true
                        }, {
                                scaleY: 1.0,
                                force3D: true
                        })
                        .staggerFromTo([$('#logo1'), $('#logo2')], 0.35, {
                                scale: 0.0,
                                force3D: true
                        }, {
                                scale: 1.0,
                                force3D: true
                        }, 0, '-=0.1')
                        .staggerFromTo([
                                [$('#team1'), $('#team2')], $('#score'), [$('#score1'), $('#score2')]
                        ], 0.35, {
                                opacity: '0'
                        }, {
                                opacity: '1'
                        }, 0.10, '-=0.35')
                        .staggerFromTo([$('#score1-box > div.circle'), $('#score2-box > div.circle')], 0.25, {
                                scale: 0.0,
                                opacity: '0',
                                force3D: true
                        }, {
                                scale: 1.0,
                                opacity: '1',
                                force3D: true
                        }, 0.0, '-=0.50');
                initNeeded = false;
        } else if (force && !tweenInitial.isActive()) {
                console.log(2);
                outroAnimation();
        } else if (force) {
                console.log(3);
                setTimeout(function() {
                        initAnimation();
                }, 1000);
        }
}

function outroAnimation() {
        if (!tweenInitial.isActive() && tweenInitial.progress() == 1) {
                tweenInitial.eventCallback("onReverseComplete", initAnimation);
                tweenInitial.delay(0);
                tweenInitial.reverse(0);
                initNeeded = true;
        }
}

function changeText(id, new_value) {
        var object = $('#' + id);
        console.log(id, new_value);
        if (data[id] == new_value) {
                return;
        } else {
                data[id] = new_value;
                storeData('data');
        }

        if (tweens[id] && tweens[id].isActive()) {
                tweens[id].kill();
        }
        tweens[id] = new TimelineMax();
        tweens[id].to(object, 0.25, {
                        opacity: 0
                })
                .call(_changeText, [object, new_value])
                .to(object, 0.25, {
                        opacity: 1
                }, "+=0.15");

        function _changeText(object, new_value) {
                object.text(new_value)
                $(document).ready(function() {
                        $('#content').find(".text-fill").textfill();
                });
        }
}

function changeImage(id, new_value) {
        var object = $('#' + id);
        if (data[id] == new_value) {
                return;
        } else {
                data[id] = new_value;
                storeData('data');
        }
        if (tweens[id] && tweens[id].isActive()) {
                tweens[id].kill();
        }
        tweens[id] = new TimelineMax();
        tweens[id].to(object, 0.35, {
                        scale: 0,
                        force3D: true
                })
                .call(_changeImage, [object, new_value])
                .to(object, 0.35, {
                        scale: 1,
                        force3D: true
                }, "+=0.25");

        function _changeImage(object, new_value) {
                object.css("background-image", "url('../" + new_value + "')");
        }
}


function changeScoreIcon(team, set, color) {
        var id = '#circle-' + team.toString() + '-' + set.toString();
        var object = $(id);
        if (tweens[id] && tweens[id].isActive()) {
                tweens[id].kill();
        }
        tweens[id] = new TimelineMax();
        tweens[id].to(object, 0.15, {
                        scale: 0,
                        opacity: '0',
                        force3D: true
                })
                .call(_changeIcon, [object, color])
                .to(object, 0.15, {
                        scale: 1,
                        opacity: '1',
                        force3D: true
                }, "+=0.05");

        function _changeIcon(object, new_value) {
                object.css("background-color", new_value);
        }
}

function setFont(newFont) {
        if (newFont == 'DEFAULT') {
                newFont = myDefaultFont;
        }
        font = newFont.trim();
        document.documentElement.style.setProperty('--font', font);
        storeData("font");
}