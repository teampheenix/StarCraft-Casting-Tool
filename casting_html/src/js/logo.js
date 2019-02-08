var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var controller = new Controller(profile, "logo", ident, false);
init();

function init() {
  loadStoredData();
  connectWebsocket();
}

function loadStoredData() {
  data = controller.loadData("data", true);
  if(data != null){
    setLogo(data["logo"]);
  }else{
    data = {};
    setLogo("casting_html/src/img/SC2.png");
  }
}

function storeData(scope = null) {
  if (scope == null || scope === "data") controller.storeData("data", data, true);
}

function setLogo(logo_url){
  if(logo_url){
    $("#img").css("background-image", "url('../" + logo_url + "')");
    data["logo"] = logo_url;
    storeData();
  }
}

function connectWebsocket() {
  console.time("connectWebsocket");
  socket = new WebSocket(controller.generateKeyURI());

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event === "DATA") {
      console.log(jsonObject.data);
      setLogo(jsonObject.data.logo);
    }
  }

  socket.onclose = function(e) {
    console.timeEnd("connectWebsocket");
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function() {
      connectWebsocket();
    }, reconnectIntervalMs);
  }
}
