// Sets the "Live App" buttons using LIVE_APP_URL from config.js
(function () {
  var url = (typeof LIVE_APP_URL !== "undefined" && LIVE_APP_URL) ? LIVE_APP_URL : "";
  if (!url) { return; }                       // no live app yet: keep the GitHub instructions link
  var links = document.querySelectorAll("a.gi-live");
  for (var i = 0; i < links.length; i++) {
    links[i].href = url;
    links[i].title = "Open the Streamlit app";
    links[i].textContent = links[i].getAttribute("data-live-text");
  }
})();
