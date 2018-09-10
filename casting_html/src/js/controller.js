class Controller {
  constructor(profile, name, ident = 0) {
    this.profile = profile;
    this.name = name;
    this.ident = ident;
    this.storage = window.localStorage;
    this.generateKey();
    this.loadCssFile(this.loadData('css'));
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
    var port = parseInt("0x".concat(this.profile), 16);
    return "ws://127.0.0.1:".concat(port, "/", path);
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
    document.getElementsByTagName("head")[0].appendChild(fileref)
    $(document).ready(function() {
      try {
        $(document).find(".text-fill").textfill();
      } catch (e) {}
    });
  }

  setStyle(file = null) {
    if (file == null) file = 'src/css/' + this.name + '/Default.css';
    if (file != this.style) {
      this.storeData('css', file);
      location.reload();
    }
  }
}
