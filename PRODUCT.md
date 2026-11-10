# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Vite, React e TypeScript no `frontend/`, consumindo a API FastAPI em `backend/app/api.py`. Essa escolha veio do plano aprovado.

## Users
Um casal usa o app pessoalmente para estudar matérias da faculdade, em uso igual no celular e no PC. Cada pessoa tem o próprio perfil, sem senha. Não é um produto comercial.

## Product Purpose
Transformar vídeos do YouTube, PDFs e documentos da faculdade em material de estudo, organizado por aluno, matéria, assunto e fontes. O aluno sabe sempre onde parou e consegue continuar de lá.

Sucesso é o aluno conseguir:
- adicionar uma aula;
- esperar o processamento;
- estudar pelo guia, pelos flashcards e pelas questões filtradas por nível e tópico;
- voltar dias depois e retomar do ponto onde parou.

## Positioning
Tudo roda localmente na GPU do casal: Whisper para transcrever e Ollama para gerar o material, sem custo por uso nem envio de dados para fora. O material é gerado do conteúdo que o próprio aluno escolheu, e os subtópicos são unificados entre todas as fontes de um assunto.

## Operating Context
O processamento é lento. Um vídeo leva de 1 a 5 minutos, porque passa pelo download, pela transcrição e pela geração. É feito um de cada vez, numa fila de um só worker, e a interface acompanha o status por polling.

O estudo acontece em sessões focadas, de leitura e de prática.

## Capabilities and Constraints
- **Hierarquia:** aluno → matéria → assunto (criado pelo aluno) → fontes (YouTube, PDF, DOCX ou TXT).
- **Guia de estudo:** visão geral e seções com os pontos principais.
- **Flashcards:** termo na frente e significado no verso. A revisão tem três respostas: errei, difícil e acertei.
- **Estudo inteligente:** questões de 4 alternativas, com nível (fácil, médio ou difícil) e subtópico, que podem ser filtradas pelos dois.
- **Progresso:** tentativas, revisões e última posição por assunto.
- **Idioma:** português do Brasil.

## Brand Commitments
O nome do app é **Acamp**.

## Evidence on Hand
Há conteúdo real gerado no banco local para teste: Biologia/Fotossíntese e Matemática/Funções do 2º grau. Não existem logo, depoimentos nem identidade visual prévia.

## Product Principles
- Estudo primeiro: a tela some e o conteúdo aparece.
- Retomar sem pensar: o "continuar de onde parei" deve estar sempre à mão.
- Processo lento deve ser visível e tranquilo, nunca ansioso.
- A mesma qualidade no celular e no PC.

## Accessibility & Inclusion
- Leitura longa confortável.
- Contraste AA.
- Tema claro e escuro.
- Alvos de toque adequados no celular.
