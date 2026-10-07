#!/usr/bin/env python3
"""Gera o e-mail marketing (boletim) do "Bate o ponto" em HTML compatível com e-mail.

Uso:
    python boletim.py slug-1 slug-2 slug-3 > boletim.html     # matérias escolhidas, nesta ordem
    python boletim.py --ultimas 6 > boletim.html             # as 6 mais recentes

A primeira matéria vira o destaque (foto grande); as demais entram em lista com miniatura.
As imagens apontam para o site publicado (baixadas e otimizadas no build do Cloudflare).
"""
from __future__ import annotations

import datetime as dt
import html
import sys

import yaml

import build

AZUL = "#0a4aa6"
AZUL_ESC = "#06306f"
TINTA = "#111a26"
CINZA = "#555f6d"
LINHA = "#e1e5eb"
FUNDO = "#f3f5f8"
SANS = "Arial, Helvetica, sans-serif"


def esc(t) -> str:
    return html.escape(str(t), quote=True)


def imagem_url(cfg: dict, m: dict) -> str:
    if m.get("imagem"):
        img = str(m["imagem"])
        if img.startswith("/"):
            return cfg["url"] + img
        return f"{cfg['url']}/imagens/{m['slug']}.jpg"  # imagem remota, baixada no build
    return f"{cfg['url']}/og/{m['slug']}.png"           # capa tipográfica


def chapeu(m: dict) -> str:
    prazo = (f' &nbsp;<span style="background:{AZUL};color:#ffffff;font-size:10px;font-weight:bold;'
             f'letter-spacing:1px;padding:2px 6px;border-radius:3px;">PRAZO</span>') if m["prazo"] else ""
    return (f'<div style="font-family:{SANS};font-size:12px;font-weight:bold;color:{AZUL};'
            f'text-transform:uppercase;letter-spacing:1px;margin:0 0 6px;">{esc(m["editoria"]["nome"])}{prazo}</div>')


def gerar(cfg: dict, materias: list[dict], hoje: dt.datetime) -> str:
    destaque, demais = materias[0], materias[1:]
    link = lambda m: f'{cfg["url"]}{m["url"]}?utm_source=boletim&amp;utm_medium=email'
    data_txt = build.data_longa(hoje)
    dia_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira",
                  "Sábado", "Domingo"][hoje.weekday()]

    itens = []
    for m in demais:
        itens.append(f'''
        <tr><td style="padding:18px 0;border-top:1px solid {LINHA};">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
            <td width="170" valign="top" style="padding-right:16px;">
              <a href="{link(m)}"><img src="{imagem_url(cfg, m)}" width="170" alt="" style="display:block;width:170px;height:auto;border-radius:6px;border:0;"></a>
            </td>
            <td valign="top">
              {chapeu(m)}
              <a href="{link(m)}" style="font-family:{SANS};font-size:18px;line-height:23px;font-weight:bold;color:{TINTA};text-decoration:none;">{esc(m["titulo"])}</a>
              <div style="font-family:{SANS};font-size:14px;line-height:21px;color:{CINZA};margin-top:6px;">{esc(m["resumo"])}</div>
            </td>
          </tr></table>
        </td></tr>''')

    prazos = [m for m in materias if m["prazo"]]
    bloco_prazos = ""
    if prazos:
        linhas = "".join(
            f'<tr><td style="padding:8px 0;border-top:1px solid #cfdcf0;font-family:{SANS};font-size:14px;line-height:20px;">'
            f'<a href="{link(m)}" style="color:{TINTA};text-decoration:none;font-weight:bold;">{esc(m["titulo"])}</a></td></tr>'
            for m in prazos)
        bloco_prazos = f'''
        <tr><td style="padding:8px 0 24px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#e8f0fb;border-left:5px solid {AZUL};border-radius:0 6px 6px 0;">
            <tr><td style="padding:16px 20px 10px;">
              <div style="font-family:{SANS};font-size:13px;font-weight:bold;color:{AZUL};text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Prazos no radar</div>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{linhas}</table>
            </td></tr>
          </table>
        </td></tr>'''

    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(cfg["nome"])} · boletim de {esc(data_txt)}</title></head>
<body style="margin:0;padding:0;background:{FUNDO};">
<div style="display:none;max-height:0;overflow:hidden;">{esc(destaque["titulo"])} e mais {len(demais)} notícias de DP.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{FUNDO};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:8px;overflow:hidden;">

  <tr><td style="background:{AZUL_ESC};padding:8px 28px;font-family:{SANS};font-size:12px;color:#cfe0f8;">{dia_semana}, {esc(data_txt)} · Boletim do DP</td></tr>
  <tr><td style="background:{AZUL};padding:22px 28px;">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="background:#ffffff;width:8px;font-size:0;line-height:0;">&nbsp;</td>
      <td style="padding-left:12px;font-family:{SANS};font-size:28px;font-weight:bold;color:#ffffff;letter-spacing:-0.5px;">{esc(cfg["nome"])}</td>
      <td style="padding-left:10px;padding-top:10px;font-family:{SANS};font-size:10px;color:#dbe7fa;letter-spacing:2px;text-transform:uppercase;" valign="bottom">por {esc(cfg["responsavel"])}</td>
    </tr></table>
  </td></tr>

  <tr><td style="padding:24px 28px 0;font-family:{SANS};font-size:15px;line-height:23px;color:{CINZA};">
    Bom dia, time! Estas são as notícias de Departamento Pessoal que importam hoje, com o que muda na nossa rotina.
  </td></tr>

  <tr><td style="padding:20px 28px 0;">
    <a href="{link(destaque)}"><img src="{imagem_url(cfg, destaque)}" width="544" alt="" style="display:block;width:100%;max-width:544px;height:auto;border-radius:8px;border:0;"></a>
    <div style="height:14px;line-height:14px;">&nbsp;</div>
    {chapeu(destaque)}
    <a href="{link(destaque)}" style="font-family:{SANS};font-size:24px;line-height:30px;font-weight:bold;color:{TINTA};text-decoration:none;">{esc(destaque["titulo"])}</a>
    <div style="font-family:{SANS};font-size:15px;line-height:23px;color:{CINZA};margin:10px 0 16px;">{esc(destaque["resumo"])}</div>
    <a href="{link(destaque)}" style="display:inline-block;background:{AZUL};color:#ffffff;font-family:{SANS};font-size:14px;font-weight:bold;text-decoration:none;padding:11px 20px;border-radius:6px;">Ler a matéria</a>
  </td></tr>

  <tr><td style="padding:24px 28px 0;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td style="font-family:{SANS};font-size:13px;font-weight:bold;color:{AZUL};text-transform:uppercase;letter-spacing:1px;padding-bottom:4px;">Mais notícias</td></tr>
      {"".join(itens)}
      {bloco_prazos}
    </table>
  </td></tr>

  <tr><td align="center" style="padding:4px 28px 28px;">
    <a href="{cfg["url"]}/?utm_source=boletim&amp;utm_medium=email" style="display:inline-block;border:2px solid {AZUL};color:{AZUL};font-family:{SANS};font-size:14px;font-weight:bold;text-decoration:none;padding:10px 22px;border-radius:6px;">Ver todas no portal</a>
  </td></tr>

  <tr><td style="background:{AZUL};padding:20px 28px;font-family:{SANS};font-size:12px;line-height:18px;color:#d6e4f8;">
    <strong style="color:#ffffff;">{esc(cfg["nome"])}</strong> · editado por {esc(cfg["responsavel"])}, {esc(cfg["responsavel_cargo"])}.<br>
    {esc(cfg["aviso_legal"])}
  </td></tr>

</table>
</td></tr></table>
</body></html>'''


def main() -> None:
    cfg = yaml.safe_load((build.RAIZ / "site.yaml").read_text(encoding="utf-8"))
    cfg["url"] = cfg["url"].rstrip("/")
    todas = build.carregar_materias(cfg, incluir_exemplos=False)
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--ultimas":
        escolhidas = todas[: int(args[1]) if len(args) > 1 else 6]
    else:
        por_slug = {m["slug"]: m for m in todas}
        faltando = [s for s in args if s not in por_slug]
        if faltando:
            sys.exit(f"matérias não encontradas: {', '.join(faltando)}")
        escolhidas = [por_slug[s] for s in args]
    if not escolhidas:
        sys.exit("nenhuma matéria para o boletim")
    sys.stdout.write(gerar(cfg, escolhidas, dt.datetime.now(build.BRT)))


if __name__ == "__main__":
    main()
