var socket = null;
var isopen = false;
var reconnectIntervalMs = 5000;
var data = {};
var duration = 0;
var countDownDate = new Date("Nov 18, 2018 13:27:00").getTime();
var interval = null;
var controller = new Controller(profile, 'countdown');

Number.prototype.pad = function(size) {
  var s = String(this);
  while (s.length < (size || 2)) {
    s = "0" + s;
  }
  return s;
}

init();

function init() {
  connectWebsocket();
  loadStoredData();
}

function count() {
  // Get todays date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;

  // Time calculations for days, hours, minutes and seconds
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // If the count down is over, write some text
  if (distance < 0) {
    printCountDown(0, 0, 0, 0);
    clearInterval(interval);
  } else {
    printCountDown(days, hours, minutes, seconds);
  }
}

function startCounter() {
  if (!data.static) {
    countDownDate = new Date().getTime() + duration + 500;
    interval = setInterval(count, 1000);
  }
}

function printCountDown(days, hours, minutes, seconds) {
  // Output the result in an element with id="demo"
  var countdownStr;
  if (days == 0 && hours == 0 && minutes == 0 && seconds == 0) {
    console.log('replacement');
    countdownStr = data.replacement;
    console.log(countdownStr);
  } else if (days > 0) {
    countdownStr = days + "d " + hours.pad() + "h " + minutes.pad() + "m " + seconds.pad() + "s";
  } else if (hours > 0) {
    countdownStr = hours.pad() + ':' + minutes.pad() + ':' + seconds.pad();
  } else {
    countdownStr = minutes + ':' + seconds.pad();
  }
  $("#countdown").text(countdownStr);
}

function loadStoredData() {
  try {
    data = controller.loadData('data', true);
    if (data) {
      processData();
    }
  } catch (e) {}
}

function dataChanged(newData) {
  if (JSON.stringify(data) === JSON.stringify(newData)) {
    return false;
  } else {
    data = newData;
    storeData();
    return true;
  }
}

function storeData(scope = null) {
  if (scope == null || scope == "data") controller.storeData('data', data, true);
}

function processData() {
  clearInterval(interval);

  $('#description').text(data.desc);
  $('#content').find(".text-fill").textfill({maxFontPixels: 80});
  if (data.static) {
    countDownDate = new Date(data.datetime).getTime();
  } else {
    var hms = data.duration.split(':')
    duration = ((parseInt(hms[0]) * 60 + parseInt(hms[1])) * 60 + parseInt(hms[2])) * 1000;
    countDownDate = new Date().getTime() + duration;
  }

  if (data.static || data.restart) {
    interval = setInterval(count, 1000);
  } else {
    clearInterval(interval);
    count();
  }

}

function connectWebsocket() {
  socket = new WebSocket(controller.generateKeyURI());

  socket.onopen = function() {
    console.log("Connected!");
    isopen = true;
  }

  socket.onmessage = function(message) {
    var jsonObject = JSON.parse(message.data);
    console.log("Message received");
    if (jsonObject.event == 'DATA') {
      if (dataChanged(jsonObject.data)) processData();
    } else if (jsonObject.event == 'CHANGE_STYLE') {
      controller.setStyle(jsonObject.data.file);
    } else if (jsonObject.event == 'START') {
      startCounter();
    } else if (jsonObject.event == 'DESC') {
      data.desc = jsonObject.data;
      $('#description').text(data.desc);
      $('#content').find(".text-fill").textfill({maxFontPixels: 80});
      storeData();
    } else if (jsonObject.event == 'RESTART') {
      data.restart = jsonObject.data;
      if (data.restart) startCounter();
      storeData();
    } else if (jsonObject.event == 'CHANGE_FONT') {
      controller.setFont(jsonObject.data.font);
    }
  }

  socket.onclose = function(e) {
    console.log("Connection closed.");
    socket = null;
    isopen = false
    setTimeout(function() {
      connectWebsocket();
    }, reconnectIntervalMs);
  }
}
