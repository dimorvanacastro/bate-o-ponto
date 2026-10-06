(function () {
  var input = document.getElementById("q");
  var status = document.getElementById("busca-status");
  var saida = document.getElementById("busca-resultados");
  var indice = null;

  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function buscar(q) {
    var termos = norm(q).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!termos.length) { status.textContent = ""; saida.innerHTML = ""; return; }
    var achados = [];
    indice.forEach(function (m) {
      var tit = norm(m.t), res = norm(m.r + " " + m.g + " " + m.e), txt = norm(m.x), pontos = 0;
      for (var i = 0; i < termos.length; i++) {
        var t = termos[i], p = 0;
        if (tit.indexOf(t) > -1) p += 5;
        if (res.indexOf(t) > -1) p += 3;
        if (txt.indexOf(t) > -1) p += 1;
        if (!p) return;
        pontos += p;
      }
      achados.push([pontos, m]);
    });
    achados.sort(function (a, b) { return b[0] - a[0]; });
    status.textContent = achados.length
      ? achados.length + (achados.length === 1 ? " resultado" : " resultados") + " para “" + q + "”."
      : "Nada encontrado para “" + q + "”. Tente outra palavra.";
    saida.innerHTML = achados.slice(0, 40).map(function (a) {
      var m = a[1];
      return '<article class="card"><p class="rotulo"><span>' + esc(m.e) + '</span></p>' +
        '<h3 class="card__titulo"><a href="' + esc(m.u) + '">' + esc(m.t) + '</a></h3>' +
        '<p class="card__resumo">' + esc(m.r) + '</p><p class="meta">' + esc(m.d) + '</p></article>';
    }).join("");
  }

  var q = new URLSearchParams(location.search).get("q") || "";
  input.value = q;
  fetch("/busca.json").then(function (r) { return r.json(); }).then(function (dados) {
    indice = dados;
    if (q) buscar(q);
    var espera;
    input.addEventListener("input", function () {
      clearTimeout(espera);
      espera = setTimeout(function () {
        buscar(input.value);
        history.replaceState(null, "", input.value ? "?q=" + encodeURIComponent(input.value) : location.pathname);
      }, 150);
    });
  }).catch(function () { status.textContent = "Não foi possível carregar a busca agora."; });
  input.focus();
})();
