var tweens = {};
var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};

data['team1'] = "Team 1";
data['team2'] = "Team 1";
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
        changeCSS("src/css/score/Alternative.css");
        insertData();
}


function insertData() {
        $('#team1').text(data['team1']);
        $('#team2').text(data['team2']);
        $('#score1').text(data['score1']);
        $('#score2').text(data['score2']);
        $('#logo1').css("background-image", 'url("../' + data['logo1'] + '")');
        $('#logo2').css("background-image", 'url("../' + data['logo2'] + '');
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
