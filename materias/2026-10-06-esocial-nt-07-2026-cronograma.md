---
titulo: "eSocial: NT 07/2026 revisada fixa datas para validar CPF de dependentes"
resumo: "A Nota Técnica S-1.3 nº 07/2026, revisada em 24 de setembro, escalona as mudanças do eSocial até janeiro de 2027. CPF de dependente passa a ser conferido na base da Receita a partir de 23 de novembro."
data: 2026-10-06T22:23:00-03:00
editoria: esocial
prazo: true
tags: ["eSocial", "Nota Técnica", "Dependentes", "Salário-paternidade"]
tema: "eSocial"
imagem: "https://imagens.ebc.com.br/LJri3GhTJ72Wf7fM-fz7eZavuAc=/1600x800/https://agenciabrasil.ebc.com.br/sites/default/files/thumbnails/image/01_carteira_de_trabalho2.jpg?itok=GzY9W8yM"
credito: "Marcello Casal Jr/Agência Brasil"
---
O eSocial, sistema pelo qual os empregadores enviam ao governo as informações trabalhistas, previdenciárias e fiscais dos empregados, publicou em **24 de setembro de 2026** a revisão da **Nota Técnica S-1.3 nº 07/2026**, que distribui os ajustes nos leiautes em cinco etapas até **18 de janeiro de 2027**. A mudança que mais pesa para o Departamento Pessoal (DP) de empresas privadas é a validação do **CPF dos dependentes na base da Receita Federal**, que entra em produção em **23 de novembro de 2026**.

## O cronograma

Cada etapa começa no ambiente de produção restrita (o ambiente de testes) e depois vai para a produção, onde os envios valem de verdade:

| Etapa | Produção restrita | Produção | O que entra |
|---|---|---|---|
| 3.2 | 25/09/2026 | 29/09/2026 | Benefícios de entes públicos (S-2410 e S-2416) |
| 3.3 | 13/10/2026 | 26/10/2026 | Novos campos no S-2500 (processo trabalhista) |
| 3.4 | 09/11/2026 | 23/11/2026 | CPF de dependente validado na Receita |
| 3.5 | 07/12/2026 | 14/12/2026 | Códigos do salário-paternidade |
| 3.6 | — | 18/01/2027 | Últimos ajustes da nota |

A etapa 3.2 já está em produção desde 29 de setembro e atinge sobretudo órgãos públicos.

## CPF de dependente: o que muda em 23 de novembro

A partir da etapa 3.4, o CPF informado para o dependente será validado na base da Receita Federal nos eventos de admissão (S-2200), alteração cadastral (S-2205), início de trabalhador sem vínculo (S-2300), pagamentos (S-1210), processo trabalhista (S-2501) e nos eventos de beneficiários de entes públicos (S-2400 e S-2405). A nota não detalha, no trecho do cronograma, se a divergência vai gerar rejeição do evento ou apenas alerta, mas o recado é claro: CPF digitado errado ou inexistente vai aparecer.

## Salário-paternidade chega ao eSocial em dezembro

A etapa 3.5 cria códigos e campos para o salário-paternidade, benefício previdenciário criado pela Lei nº 15.371/2026, cujas regras valem em sua maior parte a partir de 1º de janeiro de 2027. Entram novos códigos na Tabela 03 (natureza das rubricas), novos códigos de incidência previdenciária para o cadastro de rubricas (S-1010) e um campo próprio para o valor do salário-paternidade no totalizador S-5011. A revisão de setembro também incluiu os códigos 52 e 53 na Tabela 18 (motivos de afastamento) e mudou descrições de outros códigos por causa da mesma lei.

## Outros ajustes da revisão

A revisão excluiu a opção "I – Indeterminado (não consta CID)" do campo que indica afastamento pelo mesmo motivo no evento S-2230 (afastamento temporário). O campo passa a ser exigido somente quando houver afastamento anterior por doença, com o mesmo motivo, nos últimos 60 dias.

## E o DP com isso?

A validação de CPF vai expor cadastros antigos que nunca foram conferidos: filho lançado sem CPF correto, dependente de imposto de renda com dígito trocado, cônjuge com documento desatualizado. Se a correção ficar para depois de 23 de novembro, o problema aparece justamente na hora de enviar folha, pagamentos ou admissões.

Os códigos do salário-paternidade, por sua vez, precisam estar configurados no sistema de folha antes de janeiro, quando as novas regras da licença-paternidade começam a valer. Vale cobrar do fornecedor do software um calendário de atualização.

**Na prática:**

- Rode um relatório de dependentes e confira os CPFs na Receita antes de 23/11.
- Peça ao fornecedor da folha o cronograma de adaptação às etapas da NT 07/2026.
- Revise a parametrização de rubricas para o salário-paternidade até dezembro.
- Teste os envios na produção restrita assim que cada etapa abrir.

## Fontes

- [eSocial — Nota Técnica S-1.3 nº 07/2026 (revisada em 24/09/2026)](https://www.gov.br/esocial/pt-br/documentacao-tecnica/manuais/nota-tecnica-s-1-3-07-2026-rev.pdf)
- [eSocial — Documentação técnica](https://www.gov.br/esocial/pt-br/documentacao-tecnica)
- [Senado Federal — Lei nº 15.371, de 31 de março de 2026](https://legis.senado.leg.br/norma/42975603)
- [Contábeis — eSocial publica revisão da NT S-1.3 nº 07/2026; veja o cronograma](https://www.contabeis.com.br/noticias/79659/esocial-publica-revisao-da-nt-s-1-3-no-07-2026-veja-o-cronograma/)
