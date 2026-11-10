---
name: Acamp
description: Fichário de estudo pessoal. Aulas viram guia, fichas e questões, organizados em gavetas.
colors:
  ground: "#f1ece0"
  ground-2: "#e7e0cf"
  card: "#fbf8f0"
  ink: "#24323a"
  ink-2: "#4f5d64"
  ink-3: "#6b767a"
  rule: "#c9d6e3"
  line: "#d6ccb6"
  red: "#b8322a"
  red-soft: "#f3dcd6"
  green: "#2f6b5e"
  green-ink: "#ffffff"
  green-soft: "#d8e7df"
  amber: "#8a5a10"
  amber-soft: "#f3e4c4"
  ground-dark: "#161917"
  ground-2-dark: "#1f2421"
  card-dark: "#e9e4d8"
  ink-dark: "#e8e4da"
  ink-2-dark: "#b9b6ad"
  ink-3-dark: "#908e86"
  line-dark: "#343b37"
  rule-on-card-dark: "#cdd6dc"
  red-dark: "#e0675c"
  green-dark: "#6fb39f"
  green-ink-dark: "#0f1b17"
  amber-dark: "#e0b260"
typography:
  display:
    fontFamily: "'Source Serif 4 Variable', Georgia, serif"
    fontSize: "clamp(1.7rem, 3.6vw, 2.5rem)"
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  term:
    fontFamily: "'Source Serif 4 Variable', Georgia, serif"
    fontSize: "clamp(1.6rem, 4.2vw, 2.5rem)"
    fontWeight: 600
    lineHeight: 1.15
  title:
    fontFamily: "'Source Serif 4 Variable', Georgia, serif"
    fontSize: "clamp(1.4rem, 2.6vw, 1.9rem)"
    fontWeight: 600
    lineHeight: 1.2
  card-text:
    fontFamily: "'Source Serif 4 Variable', Georgia, serif"
    fontSize: "clamp(1.05rem, 2.2vw, 1.3rem)"
    fontWeight: 400
    lineHeight: "28px"
  reading:
    fontFamily: "'Source Serif 4 Variable', Georgia, serif"
    fontSize: "1.08rem"
    fontWeight: 400
    lineHeight: 1.7
  body:
    fontFamily: "'Public Sans Variable', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
  button:
    fontFamily: "'Public Sans Variable', system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
  label:
    fontFamily: "'Public Sans Variable', system-ui, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.09em"
  stamp:
    fontFamily: "'Public Sans Variable', system-ui, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.08em"
rounded:
  hairline: "2px"
  stamp: "3px"
  card: "4px"
  control: "6px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  card-inset: "20px"
  lg: "24px"
  ruled-line: "28px"
  xl: "32px"
  section: "48px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.green-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "0 1.1rem"
    height: "44px"
  button-default:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "0 1.1rem"
    height: "44px"
  button-ghost:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    padding: "0 1.1rem"
    height: "44px"
  button-sm:
    rounded: "{rounded.control}"
    padding: "0 .75rem"
    height: "34px"
  input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: ".55rem .8rem"
    height: "44px"
  chip:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "0 .8rem"
    height: "34px"
  chip-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
  ficha:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  drawer-head:
    backgroundColor: "{colors.card}"
    typography: "{typography.label}"
    rounded: "{rounded.card}"
    padding: ".45rem .6rem"
  tab:
    textColor: "{colors.ink-3}"
    typography: "{typography.button}"
    padding: ".7rem .9rem"
  rail:
    backgroundColor: "{colors.ground-2}"
    width: "290px"
---

# Design System: Acamp

## Overview

**Creative North Star: "O Fichário de Biblioteca"**

O Acamp é um fichário de biblioteca. Matérias são gavetas com etiqueta, assuntos são as guias dentro da gaveta, e tudo o que se estuda (flashcards, questões, o card de "Continuar", cada fonte em processamento) é uma ficha catalográfica de papel creme, com pauta azul-clara e um fio vermelho que separa o cabeçalho do corpo. A ficha é a unidade do sistema: quando algo é conteúdo de estudo, ele mora numa ficha; quando é ferramenta (filtros, formulário, abas), fica solto sobre o fundo de cartão.

A densidade é calma e de leitura. O texto de estudo é serifado (Source Serif 4) e assenta na pauta de 28px; a interface fala em sans sóbria (Public Sans), e as etiquetas de gaveta são versaletes com tracking. A cor é escassa: o verde-arquivo marca o que se clica e o que se acertou, o vermelho do fio marca o atual, o erro e o alerta, e o âmbar marca o "difícil" e o que está em andamento. No escuro, a gaveta vira carvalho escuro e as fichas continuam papel: um cinza-papel claro com a mesma tinta azul-ardósia.

O sistema recusa o painel genérico de cartões com gradiente e mascote. A profundidade vem de sombras suaves de papel sobre a mesa, nunca de sombras duras deslocadas.

**Key Characteristics:**
- A ficha catalográfica (pauta 28px + fio vermelho a 2.6rem do topo) é o contêiner de todo conteúdo de estudo.
- Flashcards em proporção real 5:3, com pilha visível atrás e virada em 3D.
- Serifa para ler, sans para operar, versalete para etiquetar.
- Uma cor de ação (verde) restrita ao clicável e ao acerto.
- Fichas continuam papel claro no tema escuro.

## Colors

Papel creme e tinta azul-ardósia, com três cores de carimbo (verde, âmbar, vermelho) usadas com parcimônia.

### Primary
- **Verde-Arquivo** (green): cor de ação e de acerto. Botão primário, foco (`outline` 2px e halo `green-soft` nos campos), barra de acertos (`meter`), seleção de texto, nível "fácil", alternativa correta e etapa concluída. No escuro sobe para green-dark com tinta green-ink-dark.

### Secondary
- **Fio Vermelho** (red): o fio horizontal de toda ficha, o sublinhado da aba ativa, a marca lateral do item atual no sumário do guia, o ponto atual da barra de progresso do quiz, os losangos dos pontos-chave, o ícone da marca, e erro (texto de erro, alternativa errada, carimbo "errei", nível "difícil").
- **Âmbar de Carimbo** (amber): "difícil" na revisão e nível "médio" nas questões; o fio da ficha pulsa em âmbar enquanto uma fonte é processada.

### Neutral
- **Cartão-Creme** (ground): fundo da mesa; também o fundo de abas fixas no mobile e de painéis.
- **Creme de Gaveta** (ground-2): trilho lateral, barra superior do mobile, controle segmentado, hover de itens.
- **Papel de Ficha** (card): superfície de toda ficha, etiqueta de gaveta, botão e campo padrão.
- **Tinta Azul-Ardósia** (ink / ink-2 / ink-3): texto principal, texto secundário (`muted`), etiquetas e texto terciário.
- **Pauta Azul-Clara** (rule): linhas da pauta dentro das fichas.
- **Fio de Bordas** (line): bordas de botões, campos, chips, painéis, divisória das abas e trilho da barra de acertos.
- **Carvalho Escuro** (ground-dark, ground-2-dark): mesa e trilho no tema escuro.
- **Cinza-Papel** (card-dark): ficha no tema escuro, com pauta rule-on-card-dark.
- Tons suaves (red-soft, green-soft, amber-soft) servem de fundo para níveis e feedback.

### Named Rules
**The Paper Stays Paper Rule.** No tema escuro só a mesa escurece. Dentro de uma ficha, o texto usa a tinta clara-tema literal (#24323a, #4f5d64, #6b767a) e não as variáveis `--ink*`, porque a ficha continua papel claro. Toda nova ficha deve fixar a tinta do papel, não herdar a da mesa.

**The Clickable Green Rule.** O verde aparece em controles clicáveis, no foco e em estados de acerto. Não pinte títulos, etiquetas ou decoração de verde.

**The Red Thread Rule.** O vermelho marca "aqui" e "errado": fio da ficha, aba ativa, item atual, erro. Ele não é cor de botão de ação.

## Typography

**Display Font:** Source Serif 4 Variable (com Georgia, serif)
**Body Font:** Public Sans Variable (com system-ui, sans-serif)

**Character:** Uma serifa de leitura para tudo que é estudo, e uma sans sóbria e neutra para tudo que é interface. As etiquetas em versalete com tracking são a voz do catálogo.

### Hierarchy
- **Display** (600, clamp(1.7rem, 3.6vw, 2.5rem), 1.12, -0.015em): título da página (assunto, "Olá", "Adicionar conteúdo").
- **Term** (600, clamp(1.6rem, 4.2vw, 2.5rem), 1.15): termo centralizado na frente do flashcard.
- **Title** (600, clamp(1.4rem, 2.6vw, 1.9rem), 1.2): título dentro da ficha ("Continuar", fim do maço). Variações próximas: seção do guia (1.4rem/1.25), nome do perfil (1.6rem/1.15), título de fonte (1.08rem/1.35), vazio (1.2rem/1.3).
- **Card text** (400, clamp(1.05rem, 2.2vw, 1.3rem), 28px): verso do flashcard, enunciado de questão (600) e visão geral do guia (1.12rem). Sempre na pauta de 28px.
- **Reading** (400, 1.08rem, 1.7): parágrafos das seções do guia, até 70ch.
- **Body** (400, 16px, 1.55): interface geral.
- **Button** (600, 0.95rem; 0.85rem no pequeno): botões, abas (0.93rem), controle segmentado.
- **Label** (600, 0.72rem, 0.09em, maiúsculas): etiqueta de gaveta, cabeçalho de ficha, `legend` de formulário.
- **Stamp** (700, 0.7rem, 0.08em, maiúsculas): carimbo de resultado e selo de nível.

### Named Rules
**The Pauta Rule.** Texto serifado dentro de uma ficha usa `line-height: 28px`, igual ao passo da pauta (linha de 1px a cada 28px, começando em 3.2rem). O texto senta na linha.

**The Label Lives In A Head Rule.** O versalete só aparece onde um fichário teria etiqueta: cabeçalho de ficha (`ficha-head`, à esquerda e à direita do fio), etiqueta de gaveta e `legend` de grupo de formulário. Ele não flutua acima de títulos de página.

**The Tabular Numbers Rule.** Contagens, datas e placares usam `font-variant-numeric: tabular-nums`.

## Layout

Grade de duas colunas no desktop: trilho lateral fixo de 290px (sticky, altura 100dvh, fundo ground-2, borda direita em line) e área principal com padding `2rem clamp(1rem, 4vw, 3.5rem) 4rem`, conteúdo até 980px centralizado. O contrato pedia 280px; o build usa 290px.

Larguras de leitura: fichas e maço até 620-640px, quiz e configuração até 760px, fontes até 820px, formulário de adicionar até 680px, parágrafos até 60-70ch. O guia usa grade de 220px (sumário sticky) + coluna fluida, com 2.5rem de vão.

Ritmo: vãos de 4, 8, 16, 20, 24, 32 e 48px; 20px (1.25rem) é a margem interna da ficha. O cabeçalho da ficha tem 2.6rem de altura e o fio vermelho fica exatamente nessa altura.

Responsivo a 860px: o trilho some, aparece a barra superior; no Início o trilho vira lista abaixo do conteúdo; as abas ficam fixas no topo do assunto; o sumário do guia some. A 560px o maço muda para 4:3.4 e a pilha aperta. Alvos de toque mínimos de 44px (34px nos pequenos, 52-56px em alternativas e avaliação).

## Elevation & Depth

Híbrido de papel sobre mesa. Superfícies de interface são planas, com borda de 1px em line. Só papel (fichas, etiquetas de gaveta, segmento ativo) tem sombra, e ela é macia e difusa, tingida com a tinta azul-ardósia. No escuro as sombras viram preto mais denso.

### Shadow Vocabulary
- **Papel na mesa** (`box-shadow: 0 1px 1px rgba(36,50,58,.06), 0 6px 18px -8px rgba(36,50,58,.25)`): toda ficha em repouso, etiqueta de gaveta, segmento ativo.
- **Papel erguido** (`box-shadow: 0 2px 3px rgba(36,50,58,.08), 0 18px 40px -16px rgba(36,50,58,.38)`): ficha do flashcard em mãos e perfil em hover.

### Named Rules
**The Soft Paper Rule.** Sombra só em papel e sempre difusa. Nunca sombra dura deslocada.

## Shapes

Cantos quase retos, como cartão cortado: 4px nas fichas e etiquetas, 6px em controles (botões, campos, painéis, segmento, feedback), 3px em carimbos e selos, 2px em barras finas, pílula só em chips e contadores. Bordas de 1px; tracejado de 1.5px na área de soltar arquivo; carimbo com borda de 1.5px em currentColor, girado -3deg. Os pontos-chave usam um losango vermelho de 7px (quadrado girado 45deg).

## Components

### Buttons
Diretos e de papel, sem gradiente.
- **Shape:** cantos suaves (6px), altura mínima 44px, padding horizontal 1.1rem, ícone a 0.5rem.
- **Primary:** fundo verde-arquivo, texto green-ink, borda da mesma cor; hover `brightness(1.08)`.
- **Default:** fundo papel (ground-2 no escuro), borda line, tinta ink; hover escurece a borda para ink-3.
- **Ghost:** transparente, tinta ink-2; hover com fundo ground-2.
- **Small:** 34px de altura, 0.85rem.
- **Active / Disabled:** desce 1px ao pressionar; desabilitado a 45% de opacidade.
- **Avaliação (Errei / Difícil / Acertei):** três botões padrão em grade, 56px, com legenda pequena; o hover pinta borda e texto na cor do resultado (vermelho, âmbar, verde). Ficam a 35% até a ficha ser virada.

### Chips
- **Style:** pílula de 34px, borda line, transparente, tinta ink-2, 0.85rem/500.
- **State:** pressionado inverte para fundo ink e texto ground. Chips de nível pressionados usam a cor do nível (verde, âmbar, vermelho).

### Cards / Containers (a Ficha)
- **Corner Style:** 4px.
- **Background:** papel (card) com pauta repetida a cada 28px a partir de 3.2rem, e o fio vermelho de 1.5px a 2.6rem do topo.
- **Shadow Strategy:** papel na mesa; papel erguido quando está em mãos.
- **Head:** linha de 2.6rem com etiquetas em versalete nas duas pontas, padding 0 1.25rem.
- **Internal Padding:** 1.25rem nas laterais.
- **Estado no fio:** em fontes processando, o fio fica âmbar e pulsa (1.6s); em erro, engrossa para 3px.
- **Painel** (não-papel): borda line, 6px, fundo ground, para ferramentas.

### Inputs / Fields
- **Style:** papel (ground-2 no escuro), borda line, 6px, 44px de altura; ícone à esquerda a 0.8rem quando houver.
- **Focus:** borda verde e halo de 3px em green-soft. Foco por teclado global: contorno verde de 2px com afastamento de 2px.
- **Controle segmentado:** trilho ground-2 com borda; o item ativo vira papel com sombra.
- **Soltar arquivo:** tracejado de 1.5px; hover verde.

### Navigation
- **Trilho:** marca serifada (700, 1.2rem) com ícone vermelho, "Adicionar conteúdo" primário, e gavetas: etiqueta de gaveta (papel, sombra, versalete com contagem) seguida dos assuntos, cada um com uma barra de acertos verde de 3px. Assunto atual com fundo ground e peso 600.
- **Abas:** texto 600 em ink-3, sublinhado vermelho de 2px no ativo; rolam na horizontal sem barra; fixas no topo no mobile.
- **Migalha:** ink-3 com chevron, acima do título do assunto.
- **Sumário do guia:** links ink-3 de 0.88rem; atual com fundo ground-2 e marca vermelha interna de 2px à esquerda.

### Flashcard (assinatura)
Maço 5:3 (4:3.4 abaixo de 560px), até 620px, com perspectiva de 1600px. Até duas fichas de pilha atrás (deslocadas 6/11px, giradas 1/2deg, 85%/60% de opacidade). A ficha entra com "deal" (0.35s, desliza 28px) e vira em Y em 0.55s `cubic-bezier(.2,.75,.25,1)`. Frente: etiqueta "Termo", carimbo do último resultado e o termo centralizado. Verso: termo e "Significado" no cabeçalho, significado na pauta. Divergência do contrato: o carimbo mostra o último resultado na frente; o carimbo de data da próxima revisão no verso não foi construído.

### Questão (estudo inteligente)
Ficha com selo de nível (fundo suave + tinta escura do nível), enunciado serifado na pauta e alternativas de 52px com letra em círculo de 26px. Acerto: borda e fundo verdes, letra cheia; erro: o mesmo em vermelho; as demais caem para 55%. O feedback sobe com "rise" (0.3s). Progresso em traços de 4px: passados ink-3, atual vermelho.

### Fonte em processamento
Ficha por fonte, com tipo e data no cabeçalho e etapas em linha (pip circular de 8px): concluídas em verde, atual em tinta 600, pendentes apagadas. Fila e erro em texto pequeno, com "Tentar de novo".

## Do's and Don'ts

### Do:
- **Do** colocar todo conteúdo de estudo numa ficha, com cabeçalho de 2.6rem, fio vermelho e pauta de 28px.
- **Do** assentar texto serifado de ficha em `line-height: 28px`.
- **Do** fixar a tinta clara-tema (#24323a) dentro das fichas para que funcionem nos dois temas.
- **Do** reservar o verde para o clicável, o foco e o acerto.
- **Do** usar Source Serif 4 para estudo e títulos, Public Sans para interface.
- **Do** manter alvos de toque de 44px ou mais e respeitar `prefers-reduced-motion`.
- **Do** usar ícones SVG de traço (lucide) a 13-18px, alinhados ao texto.

### Don't:
- **Don't** usar gradientes, mascotes ou cartões de painel genéricos; o contêiner é a ficha.
- **Don't** usar IBM Plex; a sans é Public Sans.
- **Don't** usar sombras duras deslocadas; só as duas sombras difusas de papel.
- **Don't** pôr etiqueta em versalete acima de títulos de página; ela vive no cabeçalho da ficha, na gaveta e em `legend`.
- **Don't** usar o vermelho como cor de botão de ação.
- **Don't** escurecer a ficha no tema escuro; só a mesa escurece.
