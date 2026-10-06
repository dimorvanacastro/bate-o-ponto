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
  /* toolbar: dia e hora ao vivo + "Última hora" girando */
  var relogio = document.getElementById("relogio");
  if (relogio) {
    var dias = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
    var meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
    var tique = function () {
      var d = new Date(), h = String(d.getHours()).padStart(2, "0"), mi = String(d.getMinutes()).padStart(2, "0");
      relogio.textContent = dias[d.getDay()] + ", " + (d.getDate() === 1 ? "1º" : d.getDate()) + " de " + meses[d.getMonth()] + " · " + h + "h" + mi;
    };
    tique(); setInterval(tique, 20000);
  }
  var noticias = document.querySelectorAll(".toolbar__trilho a");
  if (noticias.length > 1 && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var n = 0;
    setInterval(function () {
      noticias[n].classList.remove("ativo");
      n = (n + 1) % noticias.length;
      noticias[n].classList.add("ativo");
    }, 5000);
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

/* hero com destaques (estilo Só uma artezinha) */
(function () {
  function embaralhar(lista) {
    for (var i = lista.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = lista[i]; lista[i] = lista[j]; lista[j] = t; }
    return lista;
  }
  /* "Da semana": sorteia 4 cartões a cada visita */
  document.querySelectorAll("[data-sortear]").forEach(function (g) {
    var n = Number(g.dataset.sortear), cards = embaralhar([].slice.call(g.children));
    cards.forEach(function (c, i) { g.appendChild(c); c.hidden = i >= n; });
  });
  var hero = document.querySelector(".hero");
  if (!hero) return;
  /* destaques: ordem sorteada a cada visita (a manchete marcada fica em 1º), 5 no máximo */
  (function () {
    var todos = [].slice.call(hero.querySelectorAll(".hero__slide"));
    var fixo = todos[0].classList.contains("fixo") ? [todos[0]] : [];
    var resto = embaralhar(todos.filter(function (s) { return fixo.indexOf(s) < 0; }));
    var ordem = fixo.concat(resto), ref = hero.querySelector(".hero__controles");
    todos[0].classList.remove("ativo"); todos[0].setAttribute("aria-hidden", "true");
    ordem.forEach(function (s, i) {
      if (i >= 5) { s.remove(); return; }
      hero.insertBefore(s, ref);
      s.setAttribute("aria-label", (i + 1) + " de " + Math.min(5, ordem.length));
      s.querySelectorAll("a").forEach(function (a) { a.tabIndex = -1; });
    });
    var primeiro = ordem[0];
    primeiro.classList.add("ativo"); primeiro.removeAttribute("aria-hidden");
    primeiro.querySelectorAll("a").forEach(function (a) { a.removeAttribute("tabindex"); });
    var img = primeiro.querySelector("img[loading]"); if (img) img.loading = "eager";
  })();
  var slides = hero.querySelectorAll(".hero__slide");
  if (slides.length < 2) return;
  var pontos = hero.querySelectorAll(".hero__pontos button");
  var contador = hero.querySelector(".hero__contador b");
  var pausa = hero.querySelector(".hero__pausa");
  var reduzir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var atual = 0, timer = null, pausado = reduzir, TEMPO = 7000;

  function mostrar(i) {
    var s = slides[atual];
    s.classList.remove("ativo"); s.setAttribute("aria-hidden", "true");
    s.querySelectorAll("a").forEach(function (a) { a.tabIndex = -1; });
    pontos[atual].removeAttribute("aria-selected");
    atual = (i + slides.length) % slides.length;
    s = slides[atual];
    s.classList.add("ativo"); s.removeAttribute("aria-hidden");
    s.querySelectorAll("a").forEach(function (a) { a.removeAttribute("tabindex"); });
    pontos[atual].setAttribute("aria-selected", "true");
    if (contador) contador.textContent = String(atual + 1).padStart(2, "0");
    reiniciar();
  }
  function reiniciar() {
    clearTimeout(timer);
    hero.classList.remove("rodando");
    if (pausado) return;
    void hero.offsetWidth;
    hero.classList.add("rodando");
    timer = setTimeout(function () { mostrar(atual + 1); }, TEMPO);
  }
  pontos.forEach(function (b, i) { b.addEventListener("click", function () { mostrar(i); }); });
  hero.querySelectorAll("[data-dir]").forEach(function (b) {
    b.addEventListener("click", function () { mostrar(atual + Number(b.dataset.dir)); });
  });
  function rotuloPausa() {
    pausa.textContent = pausado ? "▶" : "❚❚";
    pausa.setAttribute("aria-label", pausado ? "Tocar destaques" : "Pausar destaques");
  }
  rotuloPausa();
  pausa.addEventListener("click", function () { pausado = !pausado; rotuloPausa(); reiniciar(); });
  hero.addEventListener("mouseenter", function () { if (!pausado) { clearTimeout(timer); hero.classList.add("parado"); } });
  hero.addEventListener("mouseleave", function () { hero.classList.remove("parado"); reiniciar(); });
  var x0 = null;
  hero.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  hero.addEventListener("touchend", function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) mostrar(atual + (dx < 0 ? 1 : -1));
    x0 = null;
  });
  reiniciar();
})();
