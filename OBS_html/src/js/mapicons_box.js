var tweens = {};
init();

function init() {
        changeCSS("src/css/mapicon_box/Square.css", 0);
        for (i = 1; i <= 8; i++) {
                $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
                loadBox(i);
        };
        setTimeout(function() {
                hideBoxs();
        }, 6000);
        setTimeout(function() {
                $('#container').empty();
                for (i = 1; i <= 3; i++) {
                        $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
                        loadBox(i);
                };
        }, 12000);
}

function showHide(i) {
        var mapicon = $("#mapicon" + i.toString());
        var image = mapicon.find("div.image");
        var race1 = mapicon.find("div.race-left");
        var race2 = mapicon.find("div.race-right");
        var player1 = mapicon.find("div.player1");
        var player2 = mapicon.find("div.player2");
        var mapname = mapicon.find("div.upper-panel");
        var maplabel = mapicon.find("div.lower-panel");
        var vs = mapicon.find("div.vs");
        mapicon.css("opacity", "0.0");
        race1.css("opacity", "0.0");
        race2.css("opacity", "0.0");
        vs.css("opacity", "0.0");
        $(document).ready(function() {
                fillBox(i);
        });
}

function fillBox(i) {
        var mapicon = "#mapicon" + i.toString();
        $(mapicon).find("span.player1").text("Player1");
        //$(mapicon).find("div.player1").addClass("winner");
        $(mapicon).find("span.player2").text("Player2");
        $(mapicon).find("span.mapname").text("Mapname");
        $(mapicon).find("span.maplabel").text("Map " + i.toString());
        $(mapicon).find("div.race-left").attr("id", "protoss");
        $(mapicon).find("div.race-right").attr("id", "zerg");
        $(mapicon).find("div.image").css("border-color", "red");
        $(mapicon).find("div.image").css("background-image", 'url("src/img/maps/Backwater.jpg")');
        $(mapicon).find(".text-fill").textfill();
        setTimeout(showBox.bind(null, i), 200 * (i - 1));
}

function showBox(i) {
        tweens[i] = new TimelineMax();
        var mapicon = $("#mapicon" + i.toString());
        var image = mapicon.find("div.image");
        var race1 = mapicon.find("div.race-left");
        var race2 = mapicon.find("div.race-right");
        var player1 = mapicon.find("div.player1");
        var player2 = mapicon.find("div.player2");
        var mapname = mapicon.find("div.upper-panel");
        var maplabel = mapicon.find("div.lower-panel");
        var vs = mapicon.find("div.vs");
        tweens[i].delay(0.5)
                .staggerTo([mapicon], 0, {
                        opacity: "1"
                }, 0.1)
                .from(image, 0.35, {
                        width: "0%",
                        border: "0px",
                        left: "50%",
                        ease: Sine.easeInOut
                })
                .staggerFrom([mapname, maplabel], 0.2, {
                        opacity: "0.0",
                        height: "0px"
                }, 0.0)
                .staggerTo([vs, [race1, race2]], 0.2, {
                        opacity: "1.0"
                }, 0.20, '=-0.2')
                .from(player1, 0.15, {
                        x: '-=110%'
                }, '=-0.15')
                .from(player2, 0.15, {
                        x: '+=110%'
                }, '=-0.15');
}

function hideBoxs() {
        for (i = 1; i <= Object.keys(tweens).length; i++) {
                var timeout = 200 * (Object.keys(tweens).length - i);
                setTimeout(hideBox.bind(null, i), timeout);
        };
}

function hideBox(i) {
        console.log(i);
        tweens[i].reverse(0);
}

function loadBox(i) {
        mapicon = "#mapicon" + i.toString();
        $(mapicon).load("data/mapicon-box-template.html", showHide.bind(null, i));
}


function changeCSS(newCssFile) {
        $('link[rel="stylesheet"]').attr('href', newCssFile);

}
