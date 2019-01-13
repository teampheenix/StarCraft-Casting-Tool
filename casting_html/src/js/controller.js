class Controller {
  constructor(profile, name, ident = 0, load_style = true) {
    this.profile = profile;
    this.name = name;
    this.ident = ident;
    this.defaultFont = null;
    this.newFont = null;
    this.font = null;
    this.storage = window.localStorage;
    this.generateKey();
    if (load_style) {
      this.loadCssFile(this.loadData('css'));
      this.setFont(this.loadData('font'));
    }
  }

  generateKey() {
    this.key = 'scct-' + this.profile + '-' + this.name;
    if (this.ident != 0) {
      this.key = this.key + '_' + this.ident.toString();
    }
  }

  generateKeyURI() {
    var path = this.name;
    if (this.ident != 0) {
      path = path + '_' + this.ident.toString();
    }
    if (window.location.hostname && window.location.hostname != 'absolute') {
      var host = window.location.hostname;
      if (window.location.port) {
        var port = window.location.port;
      } else {
        var port = 80;
      }
    } else {
      var port = parseInt("0x".concat(this.profile), 16);
      var host = 'localhost';
    }
    console.log(("ws://" + host + ":").concat(port, "/", path));
    return ("ws://" + host + ":").concat(port, "/", path);
  }

  storeData(key, value, json = false) {
    if (json) value = JSON.stringify(value);
    this.storage.setItem(this.key + '-' + key, value);
  }

  loadData(key, json = false) {
    var data = this.storage.getItem(this.key + '-' + key);
    if (json) data = JSON.parse(data);
    return data;
  }

  loadCssFile(file = null) {
    if (file == null) file = 'src/css/' + this.name + '/Default.css';
    this.style = file;
    console.log(file);
    var fileref = document.createElement("link");
    fileref.setAttribute("rel", "stylesheet");
    fileref.setAttribute("type", "text/css");
    fileref.setAttribute("href", file);
    fileref.setAttribute("onload", "controller.css_loaded()");
    document.getElementsByTagName("head")[0].appendChild(fileref);
  }

  css_loaded() {
    this.defaultFont = getComputedStyle(document.body).getPropertyValue('--font').trim();
    this.font = this.defaultFont;
    this.setFont(this.newFont);
    try {
      $(document).find(".text-fill").textfill({
        maxFontPixels: 80
      });
    } catch (e) {}
  }

  setStyle(file = null) {
    if (file == null) file = 'src/css/' + this.name + '/Default.css';
    if (file != this.style) {
      this.storeData('css', file);
      location.reload();
    }
  }

  setFont(newFont) {
    if (!newFont) return;
    if (!this.defaultFont) {
      this.newFont = newFont;
      return;
    }
    newFont = newFont.trim();
    if (newFont == 'DEFAULT' || !newFont) {
      newFont = this.defaultFont;
    }
    if (this.font != newFont) {
      console.log("Set font to " + newFont);
      document.documentElement.style.setProperty('--font', newFont);
      this.font = newFont;
    }
    this.newFont = null;
    this.storeData("font", this.font);
  }
}
