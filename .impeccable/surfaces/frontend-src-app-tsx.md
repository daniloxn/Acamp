---
version: 1
slug: "frontend-src-app-tsx"
primary_target: "frontend/src/App.tsx"
related_targets: []
---

Escopo: frontend inteiro do Acamp. Modo: Operate, com o guia em modo Read.

Público: casal universitário estudando no celular e no PC. Tarefa: adicionar aula → acompanhar processamento → estudar (guia, flashcards, estudo inteligente) → retomar.

## Direction contract
THESIS: estudo como fichário de biblioteca. Matérias são gavetas, assuntos são guias de gaveta, e flashcards são fichas catalográficas em proporção real (5:3). O app recusa o painel de cartões genérico com gradiente e mascote.

OWN-WORLD:
- **Fundo e superfícies:** fundo cartão-creme frio #f1ece0. As fichas são #fbf8f0, com pauta azul-clara e fio vermelho #b8322a no topo.
- **Cores:** tinta azul-ardósia #24323a; verde-arquivo #2f6b5e como cor de ação e de acerto; vermelho do fio para erro e alerta.
- **Tipografia:** etiquetas de gaveta em versalete com tracking, numa sans sóbria (IBM Plex fica proibida; usar "Public Sans"). Texto de estudo numa serifa de leitura ("Source Serif 4").
- **Tema escuro:** gaveta de carvalho escuro #1c1f1d com fichas em cinza-papel.

STORY: o aluno abre o app, vê as gavetas e o "Continuar" e cai direto onde parou. As fichas viram como fichas de verdade, e o processamento aparece como fichas sendo catalogadas.

FIRST VIEWPORT:
- **Desktop:** trilho esquerdo de 280px com o perfil e as matérias como gavetas com etiqueta; abaixo de cada matéria, os assuntos com uma barra fina de acertos. Na área principal, o título do assunto em serifa grande, as três abas (Guia, Flashcards, Estudo inteligente) e a ficha ativa centralizada em escala real. "Adicionar conteúdo" fica no topo do trilho.
- **Mobile:** o trilho vira uma lista no Início, e as abas ficam fixas no topo do assunto.

FORM: candidato 4 na minha lista (Ficha Catalográfica), seed:3c0f1d6302b354ef. Sinal característico: a ficha vira em 3D, com a pauta e o fio vermelho, e o carimbo de data da próxima revisão aparece no verso. As mudanças de estado ficam marcadas até serem vistas (doação do Cartão de Embarque). A cor de ação aparece só no que é clicável (doação do App Caloroso).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
