(function () {
  /* menu no celular */
  var botao = document.querySelector(".barra__menu");
  var menu = document.getElementById("menu-gaveta");
  if (botao && menu) {
    botao.addEventListener("click", function () {
      var aberto = botao.getAttribute("aria-expanded") === "true";
      botao.setAttribute("aria-expanded", String(!aberto));
      menu.classList.toggle("aberto", !aberto);
    });
  }
  /* "Há 3 horas", como nos portais de notícia */
  var agora = Date.now();
  document.querySelectorAll("time[data-rel]").forEach(function (t) {
    var d = new Date(t.getAttribute("datetime")).getTime();
    if (isNaN(d)) return;
    var min = Math.round((agora - d) / 60000);
    if (min < 0) return;
    var txt = null;
    if (min < 60) txt = "Há " + Math.max(min, 1) + (min <= 1 ? " minuto" : " minutos");
    else if (min < 60 * 24) { var h = Math.round(min / 60); txt = "Há " + h + (h === 1 ? " hora" : " horas"); }
    else if (min < 60 * 24 * 7) { var dd = Math.round(min / 1440); txt = "Há " + dd + (dd === 1 ? " dia" : " dias"); }
    if (txt) { t.title = t.textContent; t.textContent = txt; }
  });
})();
