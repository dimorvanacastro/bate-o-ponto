(function () {
  var reduzir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- destaques (hero) */
  var hero = document.querySelector(".hero");
  if (hero) {
    var slides = hero.querySelectorAll(".hero__slide");
    var pontos = hero.querySelectorAll(".hero__pontos button");
    var pausa = hero.querySelector(".hero__pausa");
    var atual = 0, timer = null, pausado = reduzir;

    function mostrar(i) {
      slides[atual].classList.remove("ativo");
      slides[atual].setAttribute("aria-hidden", "true");
      slides[atual].querySelectorAll("a").forEach(function (a) { a.tabIndex = -1; });
      if (pontos[atual]) pontos[atual].removeAttribute("aria-selected");
      atual = (i + slides.length) % slides.length;
      slides[atual].classList.add("ativo");
      slides[atual].removeAttribute("aria-hidden");
      slides[atual].querySelectorAll("a").forEach(function (a) { a.removeAttribute("tabindex"); });
      if (pontos[atual]) pontos[atual].setAttribute("aria-selected", "true");
      reiniciar();
    }
    function reiniciar() {
      clearTimeout(timer);
      hero.classList.remove("rodando");
      if (pausado || slides.length < 2) return;
      void hero.offsetWidth;
      hero.classList.add("rodando");
      timer = setTimeout(function () { mostrar(atual + 1); }, 7000);
    }
    pontos.forEach(function (b, i) { b.addEventListener("click", function () { mostrar(i); }); });
    if (pausa) {
      if (pausado) { pausa.textContent = "▶"; pausa.setAttribute("aria-label", "Tocar destaques"); }
      pausa.addEventListener("click", function () {
        pausado = !pausado;
        pausa.textContent = pausado ? "▶" : "❚❚";
        pausa.setAttribute("aria-label", pausado ? "Tocar destaques" : "Pausar destaques");
        reiniciar();
      });
    }
    hero.addEventListener("focusin", function () { clearTimeout(timer); hero.classList.remove("rodando"); });
    hero.addEventListener("focusout", reiniciar);
    var x0 = null;
    hero.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) mostrar(atual + (dx < 0 ? 1 : -1));
      x0 = null;
    });
    reiniciar();
  }

  /* ---------- fileiras com setas */
  document.querySelectorAll(".fileira").forEach(function (f) {
    var trilho = f.querySelector(".fileira__trilho");
    var setas = f.querySelector(".fileira__setas");
    if (!trilho || !setas) return;
    function atualizar() {
      var sobra = trilho.scrollWidth - trilho.clientWidth;
      setas.hidden = sobra < 8;
      setas.children[0].disabled = trilho.scrollLeft < 8;
      setas.children[1].disabled = trilho.scrollLeft > sobra - 8;
    }
    setas.addEventListener("click", function (e) {
      var b = e.target.closest(".seta");
      if (!b) return;
      trilho.scrollBy({ left: Number(b.dataset.dir) * trilho.clientWidth * 0.85, behavior: reduzir ? "auto" : "smooth" });
    });
    trilho.addEventListener("scroll", atualizar, { passive: true });
    window.addEventListener("resize", atualizar);
    atualizar();
  });

  /* ---------- topo fica sólido ao rolar */
  var topo = document.querySelector(".topo");
  function rolar() { topo.classList.toggle("solido", window.scrollY > 40); }
  window.addEventListener("scroll", rolar, { passive: true });
  rolar();
})();
