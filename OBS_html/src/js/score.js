var tweens = {};
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var tweenInitial = new TimelineMax();

data['team1'] = "Team 1";
data['team2'] = "Team 2";
data['score1'] = "1";
data['score2'] = "2";
data['logo1'] = "data/logos/64f38e.png";
data['logo2'] = "data/logos/64f38e.png";
data['sets'] = {};
data['sets'][1] = {};
data['sets'][1][1] = 'red';
data['sets'][1][2] = 'green';
data['sets'][2] = {};
data['sets'][2][1] = 'red';
data['sets'][2][2] = 'green';
data['sets'][3] = {};
data['sets'][3][1] = 'red';
data['sets'][3][2] = 'green';
data['sets'][4] = {};
data['sets'][4][1] = 'grey';
data['sets'][4][2] = 'grey';
data['sets'][5] = {};
data['sets'][5][1] = 'grey';
data['sets'][5][2] = 'grey';

init();

function init() {
        //connectWebsocket();
        changeCSS("src/css/score/Minimal.css");
        initHide();
        insertData();
        initAnimation();
        setTimeout(function() {
                changeText('team1', "team pheeniX");
        }, 2000);
        setTimeout(function() {
                changeText('team2', "MindGaming");
        }, 3000);
        setTimeout(function() {
                changeText('score1', "3");
        }, 4000);
        setTimeout(function() {
                changeText('score2', "4");
        }, 4500);
        setTimeout(function() {
                changeImage('logo1', "data/logos/679f86.png");
                changeScoreIcon(1, 4, 'green')
                changeScoreIcon(2, 4, 'red')
        }, 4000);
}


function insertData() {
        $('#team1').text(data['team1']);
        $('#team2').text(data['team2']);
        $('#score1').text(data['score1']);
        $('#score2').text(data['score2']);
        $('#logo1').css("background-image", "url('../" + data['logo1'] + "')");
        $('#logo2').css("background-image", "url('../" + data['logo1'] + "')");
        insertIcons();
        $(document).ready(function() {
                $('#content').find(".text-fill").textfill();
        });
}

function insertIcons() {
        for (var i = 1; i <= Object.keys(data['sets']).length; i++) {
                for (var j = 1; j <= 2; j++) {
                        var color = data['sets'][i][j];
                        $('#score' + j.toString() + '-box').append('<div class="circle" id="circle-' + j.toString() + '-' + i.toString() + '" style="background-color: ' + color + '"></div>');
                }
        }
}

function changeCSS(newCssFile) {
        console.log('CSS file changed to', newCssFile);
        $('link[rel="stylesheet"]').attr('href', newCssFile);

}

function initHide() {
        var content = document.getElementById("content");
        content.style.setProperty('visibility', 'visible');
        tweenInitial.staggerTo([content], 0, {
                opacity: "0"
        }, 0);
}

function initAnimation() {
        tweenInitial = new TimelineMax();
        var content = $('#content');
        var box = $('#box');
        tweenInitial.delay(0.5)
                .staggerTo([content], 0, {
                        opacity: "1"
                }, 0)
                .from(box, 0.35, {
                        scaleY: 0.0,
                        force3D: true
                })
                .staggerFrom([$('#logo1'), $('#logo2')], 0.35, {
                        scale: 0.0,
                        force3D: true
                }, 0, '-=0.1')
                .staggerFrom([
                        [$('#team1'), $('#team2')], $('#score'), [$('#score1'), $('#score2')]
                ], 0.35, {
                        opacity: '0'
                }, 0.10, '-=0.35')
                .staggerFrom([$('#score1-box > div.circle'), $('#score2-box > div.circle')], 0.25, {
                        scale: 0.0,
                        opacity: '0',
                        force3D: true
                }, 0.0, '-=0.50');
}

function changeText(id, new_value) {
        var object = $('#' + id);
        var tween = new TimelineMax();
        tween.to(object, 0.25, {
                        opacity: 0
                })
                .call(_changeText, [object, new_value])
                .to(object, 0.25, {
                        opacity: 1
                }, "+=0.15");

        function _changeText(object, new_value) {
                object.text(new_value)
        }
}

function changeImage(id, new_value) {
        var object = $('#' + id);
        var tween = new TimelineMax();
        tween.to(object, 0.35, {
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
        var object = $('#circle-' + team.toString() + '-' + set.toString());
        var tween = new TimelineMax();
        tween.to(object, 0.15, {
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
