(function(){
  if (!window.bookmarklet) {
    var bookmarklet_js = document.body.appendChild(document.createElement("script"));
    bookmarklet_js.src = "//10.0.0.105:8000/static/js/bookmarklet.js?r=" + Math.floor(Math.random() * 9999999999999999);
    window.bookmarklet = true;
  } else {
    bookmarkletLaunch();
  }
})();
