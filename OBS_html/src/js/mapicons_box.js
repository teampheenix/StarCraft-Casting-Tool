window.onload = function() {
        init();
}

function init() {
        changeCSS("src/css/mapicon_box/Square.css", 0);
        for (i = 1; i <= 1; i++) {
                $('#container').append("<div class='block' id='mapicon" + i.toString() + "'></div>");
                loadBox(i);
        };
}

function showHide(i) {
        mapicon = "#mapicon" + i.toString();
        if ($(mapicon).find("div.image").css("visibility") == "hidden") {
                $(mapicon).css("display", "none");
        } else {
                $(mapicon).css("display", "inline-block");
        }

        //$(mapicon).find(".text-fill").textfill();
        fillBox(i);
}

function fillBox(i){
        mapicon = "#mapicon" + i.toString();
        $(mapicon).find("span.player1").text("Player1");
        $(mapicon).find("div.player1").addClass("winner");
        $(mapicon).find("span.player2").text("Player2");
        $(mapicon).find("span.mapname").text("Mapname");
        $(mapicon).find("span.maplabel").text("Label");
        $(mapicon).find("div.race-left").attr("id","protoss");
        $(mapicon).find("div.race-right").attr("id","zerg");
        $(mapicon).find("img.map").attr("src","src/img/maps/Abiogenesis.jpg");
        $(mapicon).find("div.image").css("border-color", "red");
        $(mapicon).find("div.text-fill").textfill();

}

function loadBox(i) {
        mapicon = "#mapicon" + i.toString();
        $(mapicon).load("data/mapicon-box-template.html", showHide.bind(null, i));
}


function changeCSS(newCssFile, cssLinkIndex) {
        var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);
        var newlink = document.createElement("link");
        newlink.setAttribute("rel", "stylesheet");
        newlink.setAttribute("type", "text/css");
        newlink.setAttribute("href", newCssFile);
        if (newCssFile && newCssFile != "null") {
                console.log(newCssFile);
                cssFile = newCssFile;
                if (oldlink.href != newlink.href) {
                        document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
                }
        }

}
