#!/usr/bin/env python3
"""Gera o site estático do portal "Bate o ponto".

Uso:
    python build.py              # gera o site em _site/ com as matérias de materias/
    python build.py --exemplos   # inclui também as matérias de exemplo (só para prévia local)

Cada matéria é um arquivo Markdown em materias/AAAA-MM-DD-slug.md com cabeçalho YAML:

    ---
    titulo: "INSS 2027: veja as novas faixas de contribuição"
    resumo: "Linha fina de 1 ou 2 frases."
    data: 2027-01-12T08:00:00-03:00
    atualizado: 2027-01-13T10:30:00-03:00   # opcional
    nota_atualizacao: "Texto curto do que mudou."  # opcional
    editoria: folha            # slug de uma editoria do site.yaml
    prazo: true                # opcional: tem data-limite para o DP
    tags: [INSS, Folha]
    tema: INSS                 # nome curto que vai na capa tipográfica
    imagem: /imagens/slug.jpg  # opcional (só imagem oficial)
    credito: "Divulgação/MTE"  # obrigatório se houver imagem
    manchete: true             # opcional: vira a manchete da home
    ---
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import math
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "_site"
BRT = dt.timezone(dt.timedelta(hours=-3))
POR_PAGINA = 24

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


# ---------------------------------------------------------------- utilidades
def slugify(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "item"


def como_data(valor) -> dt.datetime:
    if isinstance(valor, dt.datetime):
        d = valor
    elif isinstance(valor, dt.date):
        d = dt.datetime(valor.year, valor.month, valor.day, 8, 0)
    else:
        d = dt.datetime.fromisoformat(str(valor))
    if d.tzinfo is None:
        d = d.replace(tzinfo=BRT)
    return d.astimezone(BRT)


def data_longa(d: dt.datetime) -> str:
    dia = "1º" if d.day == 1 else str(d.day)
    return f"{dia} de {MESES[d.month - 1]} de {d.year}"


def data_curta(d: dt.datetime) -> str:
    return f"{d.day:02d} {MESES_CURTO[d.month - 1]} {d.year}"


def hora(d: dt.datetime) -> str:
    return f"{d.hour:02d}h{d.minute:02d}"


def tom(texto: str) -> int:
    """Escolhe 1 de 3 tons de azul para a capa tipográfica, sempre o mesmo para o mesmo tema."""
    return int(hashlib.md5(texto.encode()).hexdigest(), 16) % 3


def ler_frontmatter(caminho: Path) -> tuple[dict, str]:
    bruto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", bruto, re.S)
    if not m:
        raise ValueError(f"{caminho.name}: falta o cabeçalho YAML entre ---")
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


# ---------------------------------------------------------------- markdown
def md_para_html(texto: str) -> str:
    corpo = markdown.markdown(
        texto,
        extensions=["extra", "sane_lists", "smarty"],
        extension_configs={"smarty": {"substitutions": {
            "left-double-quote": "“", "right-double-quote": "”",
            "left-single-quote": "‘", "right-single-quote": "’"}}},
        output_format="html",
    )
    # tabelas com rolagem horizontal no celular
    corpo = re.sub(r"<table>", '<div class="tabela"><table>', corpo)
    corpo = re.sub(r"</table>", "</table></div>", corpo)
    # links externos
    corpo = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', corpo)
    # "E o DP com isso?" vira o bloco de análise
    corpo = re.sub(
        r"<h2[^>]*>\s*E o DP com isso\s*\??\s*</h2>(.*?)(?=<h2[\s>]|$)",
        lambda m: ('<aside class="analise" aria-labelledby="analise-titulo">'
                   '<p class="analise__rotulo">Análise</p>'
                   '<h2 id="analise-titulo">E o DP com isso?</h2>' + m.group(1) + "</aside>"),
        corpo, count=1, flags=re.S | re.I)
    # "Fontes"
    corpo = re.sub(
        r"<h2[^>]*>\s*Fontes\s*</h2>(.*?)(?=<h2[\s>]|$)",
        lambda m: '<section class="fontes"><h2>Fontes</h2>' + m.group(1) + "</section>",
        corpo, count=1, flags=re.S | re.I)
    return corpo


def texto_puro(html_txt: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", html_txt))).strip()


# ---------------------------------------------------------------- capa (imagem social)
def gerar_og(destino: Path, tema: str, titulo: str, nome_site: str, t: int) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:  # sem Pillow, segue sem imagem social própria
        return
    fundos = [(18, 53, 91), (29, 95, 160), (11, 34, 61)]
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), fundos[t])
    d = ImageDraw.Draw(img)
    fonte_b = RAIZ / "assets/fonts/Archivo-Bold.ttf"
    fonte_m = RAIZ / "assets/fonts/Archivo-Medium.ttf"
    f_tema = ImageFont.truetype(str(fonte_b), 40)
    f_tit = ImageFont.truetype(str(fonte_b), 62)
    f_site = ImageFont.truetype(str(fonte_m), 30)
    x = 80
    d.rectangle([x, 92, x + 14, 132], fill=(255, 255, 255))
    d.text((x + 34, 88), tema.upper(), font=f_tema, fill=(205, 222, 242))
    # quebra o título em linhas
    palavras, linhas, atual = titulo.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=f_tit) <= W - 2 * x:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    if len(linhas) > 4:
        linhas = linhas[:4]
        linhas[-1] = linhas[-1].rstrip(".,;:") + "…"
    y = 190
    for linha in linhas:
        d.text((x, y), linha, font=f_tit, fill=(255, 255, 255))
        y += 76
    d.line([x, H - 100, W - x, H - 100], fill=(255, 255, 255), width=2)
    d.text((x, H - 80), nome_site, font=f_site, fill=(255, 255, 255))
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, "PNG", optimize=True)


# ---------------------------------------------------------------- stories 1080x1920
def _quebrar(d, texto, fonte, largura):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def gerar_story(destino: Path, m: dict, cfg: dict) -> None:
    """Story vertical para Instagram: marca no topo, capa, editoria, título e área livre para o adesivo de link."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError:
        return
    W, H, X = 1080, 1920, 72
    azul, azul_esc = (10, 74, 166), (6, 42, 94)
    img = Image.new("RGB", (W, H), azul_esc)
    d = ImageDraw.Draw(img)
    # leve degradê vertical
    for y in range(H):
        t = y / H
        cor = tuple(int(azul[i] * (1 - t) + azul_esc[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=cor)
    fb = str(RAIZ / "assets/fonts/Archivo-Bold.ttf")
    fm = str(RAIZ / "assets/fonts/Archivo-Medium.ttf")
    F = lambda f, n: ImageFont.truetype(f, n)
    # marca
    d.rectangle([X, 150, X + 16, 210], fill=(255, 255, 255))
    d.text((X + 40, 146), cfg["nome"], font=F(fb, 64), fill=(255, 255, 255))
    d.text((X, 250), cfg["tagline"].upper(), font=F(fm, 26), fill=(169, 203, 255))
    # capa (16:10)
    cx0, cy0, cw, ch = X, 330, W - 2 * X, int((W - 2 * X) * 10 / 16)
    foto = None
    if m.get("imagem") and str(m["imagem"]).startswith("/"):
        arq = RAIZ / str(m["imagem"]).lstrip("/")
        if arq.exists():
            try:
                foto = ImageOps.fit(Image.open(arq).convert("RGB"), (cw, ch))
            except Exception:
                foto = None
    if foto:
        img.paste(foto, (cx0, cy0))
        if m.get("credito"):
            fc = F(fm, 22)
            txt = str(m["credito"]).upper()
            tw = d.textlength(txt, font=fc)
            d.rectangle([cx0 + cw - tw - 32, cy0 + ch - 44, cx0 + cw, cy0 + ch], fill=(6, 42, 94))
            d.text((cx0 + cw - tw - 16, cy0 + ch - 37), txt, font=fc, fill=(220, 232, 250))
    else:
        caixa = Image.new("RGB", (cw, ch))
        cd = ImageDraw.Draw(caixa)
        tons = [((15, 58, 120), (47, 127, 224)), ((8, 58, 130), (31, 104, 201)), ((13, 91, 196), (87, 160, 240))][m["tom"]]
        for x in range(cw):
            t = x / cw
            cd.line([(x, 0), (x, ch)], fill=tuple(int(tons[0][i] * (1 - t) + tons[1][i] * t) for i in range(3)))
        cd.ellipse([cw * 0.55, -ch * 0.45, cw * 1.25, ch * 0.75], fill=None, outline=(255, 255, 255), width=2)
        tam = 150
        ft = F(fb, tam)
        while cd.textlength(m["tema"], font=ft) > cw - 96 and tam > 60:
            tam -= 8
            ft = F(fb, tam)
        cd.text((48, ch - 48 - tam), m["tema"], font=ft, fill=(255, 255, 255))
        img.paste(caixa, (cx0, cy0))
    # editoria
    y = cy0 + ch + 64
    rot = m["editoria"]["nome"].upper() + ("  ·  PRAZO" if m["prazo"] else "")
    d.text((X, y), rot, font=F(fb, 30), fill=(169, 203, 255))
    # título
    y += 64
    tam = 76
    while True:
        ft = F(fb, tam)
        linhas = _quebrar(d, m["titulo"], ft, W - 2 * X)
        if len(linhas) <= 5 or tam <= 52:
            break
        tam -= 4
    for ln in linhas[:6]:
        d.text((X, y), ln, font=ft, fill=(255, 255, 255))
        y += int(tam * 1.16)
    # rodapé (a área entre o título e o rodapé fica livre para o adesivo de link)
    d.line([(X, H - 190), (W - X, H - 190)], fill=(120, 160, 220), width=2)
    fr = F(fm, 26)
    d.text((X, H - 160), ("Por " + cfg["responsavel"]).upper(), font=fr, fill=(200, 218, 245))
    dominio = cfg["url"].split("//", 1)[-1].upper()
    d.text((W - X - d.textlength(dominio, font=fr), H - 160), dominio, font=fr, fill=(200, 218, 245))
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, "JPEG", quality=88, optimize=True, progressive=True)


# ---------------------------------------------------------------- carga
def carregar_materias(cfg: dict, incluir_exemplos: bool) -> list[dict]:
    pastas = [RAIZ / "materias"] + ([RAIZ / "exemplos"] if incluir_exemplos else [])
    editorias = {e["slug"]: e for e in cfg["editorias"]}
    materias, slugs = [], set()
    for pasta in pastas:
        for arq in sorted(pasta.glob("*.md")):
            meta, corpo_md = ler_frontmatter(arq)
            for campo in ("titulo", "resumo", "data", "editoria"):
                if not meta.get(campo):
                    raise ValueError(f"{arq.name}: falta o campo '{campo}'")
            if meta["editoria"] not in editorias:
                raise ValueError(f"{arq.name}: editoria '{meta['editoria']}' não existe no site.yaml")
            slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", arq.stem)
            slug = slugify(slug)
            if slug in slugs:
                raise ValueError(f"{arq.name}: endereço repetido '{slug}'")
            slugs.add(slug)
            corpo = md_para_html(corpo_md)
            palavras = len(texto_puro(corpo).split())
            data = como_data(meta["data"])
            atualizado = como_data(meta["atualizado"]) if meta.get("atualizado") else None
            tema = str(meta.get("tema") or (meta.get("tags") or [editorias[meta["editoria"]]["nome"]])[0])
            m = {
                "arquivo": arq.name,
                "slug": slug,
                "url": f"/{slug}/",
                "titulo": str(meta["titulo"]).strip(),
                "resumo": str(meta["resumo"]).strip(),
                "data": data,
                "atualizado": atualizado if atualizado and atualizado > data else None,
                "nota_atualizacao": meta.get("nota_atualizacao"),
                "editoria": editorias[meta["editoria"]],
                "prazo": bool(meta.get("prazo")),
                "tags": [str(t) for t in (meta.get("tags") or [])],
                "tema": tema,
                "tom": tom(tema),
                "imagem": meta.get("imagem"),
                "credito": meta.get("credito"),
                "manchete": bool(meta.get("manchete")),
                "exemplo": pasta.name == "exemplos",
                "corpo": corpo,
                "leitura": max(1, math.ceil(palavras / 200)),
            }
            materias.append(m)
    materias.sort(key=lambda m: m["data"], reverse=True)
    return materias


def carregar_paginas() -> list[dict]:
    paginas = []
    for arq in sorted((RAIZ / "paginas").glob("*.md")):
        meta, corpo_md = ler_frontmatter(arq)
        slug = slugify(meta.get("slug") or arq.stem)
        paginas.append({"slug": slug, "url": f"/{slug}/", "titulo": meta["titulo"],
                        "resumo": meta.get("resumo", ""), "corpo": md_para_html(corpo_md),
                        "rodape": bool(meta.get("rodape", True))})
    return paginas


# ---------------------------------------------------------------- saída
def escrever(caminho_url: str, conteudo: str) -> None:
    destino = SAIDA / caminho_url.lstrip("/")
    if caminho_url.endswith("/"):
        destino = destino / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")


def paginar(itens: list, base: str):
    total = max(1, math.ceil(len(itens) / POR_PAGINA))
    for i in range(total):
        url = base if i == 0 else f"{base}pagina/{i + 1}/"
        anterior = None if i == 0 else (base if i == 1 else f"{base}pagina/{i}/")
        proxima = f"{base}pagina/{i + 2}/" if i + 1 < total else None
        yield url, itens[i * POR_PAGINA:(i + 1) * POR_PAGINA], {
            "atual": i + 1, "total": total, "anterior": anterior, "proxima": proxima}


def main() -> None:
    incluir_exemplos = "--exemplos" in sys.argv
    cfg = yaml.safe_load((RAIZ / "site.yaml").read_text(encoding="utf-8"))
    cfg["url"] = cfg["url"].rstrip("/")
    agora = dt.datetime.now(BRT)

    materias = carregar_materias(cfg, incluir_exemplos)
    paginas = carregar_paginas()

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    SAIDA.mkdir()
    shutil.copytree(RAIZ / "assets", SAIDA / "assets")
    if (RAIZ / "imagens").exists():
        shutil.copytree(RAIZ / "imagens", SAIDA / "imagens")
    for estatico in (RAIZ / "estatico").glob("*") if (RAIZ / "estatico").exists() else []:
        shutil.copy(estatico, SAIDA / estatico.name)

    # imagem social de cada matéria
    for m in materias:
        if m["imagem"]:
            m["og"] = m["imagem"]
        else:
            m["og"] = f"/og/{m['slug']}.png"
            gerar_og(SAIDA / "og" / f"{m['slug']}.png", m["tema"], m["titulo"], cfg["nome"], m["tom"])
    gerar_og(SAIDA / "og" / "site.png", "Departamento Pessoal", cfg["tagline"], cfg["nome"], 0)

    # stories 1080x1920 das matérias dos últimos 30 dias (em /stories/<slug>.jpg)
    for m in materias:
        if agora - m["data"] <= dt.timedelta(days=30):
            gerar_story(SAIDA / "stories" / f"{m['slug']}.jpg", m, cfg)
            m["story"] = f"/stories/{m['slug']}.jpg"

    env = Environment(loader=FileSystemLoader(RAIZ / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.filters.update(slugify=slugify, data_longa=data_longa, data_curta=data_curta, hora=hora,
                       iso=lambda d: d.isoformat(timespec="seconds"))
    env.globals.update(site=cfg, agora=agora, paginas_rodape=[p for p in paginas if p["rodape"]],
                       ano=agora.year, exemplos=incluir_exemplos,
                       versao=hashlib.md5(b"".join(f.read_bytes() for f in sorted((RAIZ / "assets").glob("*.*")))).hexdigest()[:8])

    def render(tpl: str, url: str, **ctx) -> None:
        ctx.setdefault("canonical", cfg["url"] + url)
        ctx.setdefault("url_atual", url)
        escrever(url, env.get_template(tpl).render(**ctx))

    # home: hero inteiro com 5 destaques + "Da semana" + feed de últimas com lateral de prazos
    manchete = next((m for m in materias if m["manchete"]), materias[0] if materias else None)
    # o hero mostra 5 por visita, sorteados (no navegador) entre os 8 mais recentes; a manchete marcada fica sempre em 1º
    destaques = ([manchete] + [m for m in materias if m is not manchete][:7]) if manchete else []
    def fora(m, *grupos):
        return not any(m is x for g in grupos for x in g)
    semana = [m for m in materias if fora(m, destaques[:5]) and agora - m["data"] <= dt.timedelta(days=10)][:12]
    if len(semana) < 4:
        semana = [m for m in materias if fora(m, destaques[:5])][:8]
    # o feed mostra tudo em ordem cronológica (inclusive o que está no hero), como nos portais
    ultimas = materias[:15]
    prazos = [m for m in materias if m["prazo"]][:6]
    render("home.html", "/", destaques=destaques, semana=semana, ultimas=ultimas, prazos=prazos)

    # matérias
    for i, m in enumerate(materias):
        relacionadas = [o for o in materias if o is not m and o["editoria"] is m["editoria"]][:4]
        if len(relacionadas) < 4:
            relacionadas += [o for o in materias if o is not m and not any(o is r for r in relacionadas)][:4 - len(relacionadas)]
        render("materia.html", m["url"], m=m, relacionadas=relacionadas)

    # editorias
    for e in cfg["editorias"]:
        itens = [m for m in materias if m["editoria"]["slug"] == e["slug"]]
        for url, pagina, pag in paginar(itens, f"/editoria/{e['slug']}/"):
            render("lista.html", url, titulo=e["nome"], subtitulo=None, itens=pagina, pag=pag,
                   editoria_atual=e["slug"])
    # prazos
    itens = [m for m in materias if m["prazo"]]
    for url, pagina, pag in paginar(itens, "/prazos/"):
        render("lista.html", url, titulo="Prazos",
               subtitulo="Notícias com data-limite para o Departamento Pessoal.",
               itens=pagina, pag=pag, editoria_atual="prazos")
    # todas
    for url, pagina, pag in paginar(materias, "/todas/"):
        render("lista.html", url, titulo="Todas as notícias", subtitulo=None, itens=pagina, pag=pag,
               editoria_atual="todas")
    # tags
    tags: dict[str, list] = {}
    for m in materias:
        for t in m["tags"]:
            tags.setdefault(slugify(t), [t, []])[1].append(m)
    for slug, (nome, itens) in tags.items():
        for url, pagina, pag in paginar(itens, f"/tema/{slug}/"):
            render("lista.html", url, titulo=nome, subtitulo="Tema", itens=pagina, pag=pag,
                   editoria_atual=None)

    # páginas fixas, busca e 404
    for p in paginas:
        render("pagina.html", p["url"], p=p)
    render("busca.html", "/busca/")
    render("404.html", "/404.html", canonical=None)

    # índice da busca
    indice = [{"t": m["titulo"], "r": m["resumo"], "u": m["url"], "e": m["editoria"]["nome"],
               "d": data_curta(m["data"]), "g": " ".join(m["tags"]),
               "x": texto_puro(m["corpo"])[:1500]} for m in materias]
    (SAIDA / "busca.json").write_text(json.dumps(indice, ensure_ascii=False), encoding="utf-8")

    # feed RSS
    itens_rss = []
    for m in materias[:30]:
        itens_rss.append(
            f"<item><title>{xml_escape(m['titulo'])}</title><link>{cfg['url']}{m['url']}</link>"
            f"<guid isPermaLink=\"true\">{cfg['url']}{m['url']}</guid>"
            f"<pubDate>{m['data'].strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>"
            f"<category>{xml_escape(m['editoria']['nome'])}</category>"
            f"<description>{xml_escape(m['resumo'])}</description></item>")
    (SAIDA / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        f"<title>{xml_escape(cfg['nome'])}</title><link>{cfg['url']}/</link>"
        f"<description>{xml_escape(cfg['tagline'])}</description><language>pt-br</language>"
        + "".join(itens_rss) + "</channel></rss>", encoding="utf-8")

    # sitemaps
    urls = [("/", agora)] + [(m["url"], m["atualizado"] or m["data"]) for m in materias]
    urls += [(f"/editoria/{e['slug']}/", agora) for e in cfg["editorias"]]
    urls += [("/todas/", agora), ("/prazos/", agora)] + [(p["url"], None) for p in paginas]
    linhas = []
    for u, d in urls:
        lastmod = f"<lastmod>{d.isoformat(timespec='seconds')}</lastmod>" if d else ""
        linhas.append(f"<url><loc>{cfg['url']}{u}</loc>{lastmod}</url>")
    (SAIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(linhas) + "</urlset>",
        encoding="utf-8")
    recentes = [m for m in materias if agora - m["data"] <= dt.timedelta(hours=48)]
    noticias = "".join(
        f"<url><loc>{cfg['url']}{m['url']}</loc><news:news><news:publication>"
        f"<news:name>{xml_escape(cfg['nome'])}</news:name><news:language>pt</news:language>"
        f"</news:publication><news:publication_date>{m['data'].isoformat(timespec='seconds')}"
        f"</news:publication_date><news:title>{xml_escape(m['titulo'])}</news:title></news:news></url>"
        for m in recentes)
    (SAIDA / "sitemap-noticias.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">' + noticias + "</urlset>",
        encoding="utf-8")

    # robots.txt: buscadores e robôs de busca de IA liberados
    (SAIDA / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {cfg['url']}/sitemap.xml\nSitemap: {cfg['url']}/sitemap-noticias.xml\n",
        encoding="utf-8")
    if cfg.get("adsense_id"):
        pub = cfg["adsense_id"].replace("ca-", "")
        (SAIDA / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")

    # cabeçalhos do Cloudflare Pages (cache)
    (SAIDA / "_headers").write_text(
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/og/*\n  Cache-Control: public, max-age=86400\n"
        "/imagens/*\n  Cache-Control: public, max-age=2592000\n"
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8")

    print(f"OK: {len(materias)} matérias, {len(paginas)} páginas fixas → {SAIDA}")


if __name__ == "__main__":
    main()
