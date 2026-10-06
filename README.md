# Bate o ponto

Portal de notícias de Departamento Pessoal. Site estático publicado pelo Cloudflare Pages.

## Como funciona

- Cada matéria é um arquivo Markdown em `materias/AAAA-MM-DD-slug.md` (formato no topo de `build.py`).
- A tarefa agendada diária grava a matéria nessa pasta pelo GitHub; o Cloudflare Pages gera o site sozinho em cerca de 1 minuto.
- Imagens de capa (só oficiais) vão em `imagens/`. Sem imagem, o site gera uma capa tipográfica com o campo `tema`.
- Configurações (nome, endereço, editorias, Analytics, AdSense) ficam em `site.yaml`.

## Cloudflare Pages

- Comando de build: `python build.py`
- Pasta de saída: `_site`
- Variável de ambiente: `PYTHON_VERSION = 3.12`

## Prévia local

```
pip install -r requirements.txt
python build.py --exemplos
python -m http.server -d _site
```

A pasta `exemplos/` só entra no site com `--exemplos` e nunca vai ao ar.
