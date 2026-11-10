# Acamp — passagem de bastão

Este documento existe para que outra sessão do Claude, rodando no **Linux**, leia e continue o trabalho. Ele junta o que já foi feito, o que falta e as decisões tomadas até agora.

- **Repositório:** https://github.com/daniloxn/Acamp
- **Leia também:** `README.md` (como rodar), `PRODUCT.md` e `DESIGN.md` (produto e visual) e o `CLAUDE.md` da pasta acima (as decisões de arquitetura originais).

## 1. Intuito do app
App de estudo pessoal, usado só pelo casal. Não é produto comercial. Você manda uma fonte e ele gera o material de estudo.
- **Fontes aceitas:** link do YouTube, PDF, DOCX ou TXT.
- **O que ele gera:** guia de estudo, flashcards e questões por nível (o "estudo inteligente").
- **Organização:** aluno → matéria → assunto → fontes.
- **Progresso:** guarda acertos, revisões de flashcards e o "continuar de onde parei".

Tudo roda **localmente**, sem serviços pagos:
- a transcrição usa Whisper na GPU;
- a geração usa uma IA local no Ollama.

## 2. Arquitetura atual
```
YouTube → yt-dlp (áudio) → faster-whisper medium/float16 (GPU) → cache data/transcripts/{video_id}.json
PDF/DOCX/TXT → pymupdf / python-docx → texto
texto → Ollama qwen3:8b (JSON validado com Pydantic, schema v2) → SQLite data/estudo.db (+ backup data/study/source_{id}.json)
FastAPI (backend/app/api.py) + worker único em fila (backend/app/worker.py) → frontend React (frontend/, servido de frontend/dist)
```

- **Hardware:** RTX 5050 com 8 GB de VRAM (Blackwell, `sm_120`).
- **Regra fixa do usuário:** o Whisper e a IA **nunca rodam ao mesmo tempo**. Um termina para o outro começar. Hoje isso é garantido assim:
  - a transcrição roda num subprocesso, que libera a VRAM ao terminar;
  - o Ollama usa `keep_alive=0`;
  - o pipeline confere a VRAM entre as etapas;
  - há um único worker e o `GPU_LOCK`.
- **Banco SQLModel/SQLite.** Tabelas: `student`, `subject`, `topic`, `source`, `subtopic`, `topicprogress`, `study_guide`, `flashcard`, `question`, `questionattempt` e `flashcardreview`.
- **Frontend:** Vite + React + TS, no visual "Ficha Catalográfica":
  - papel creme com pauta azul e fio vermelho;
  - fontes Source Serif 4 e Public Sans;
  - tema claro e escuro;
  - funciona no celular, na mesma rede, por `http://<ip-do-pc>:8000`.

## 3. O que já foi implementado
1. **Ambiente CUDA validado** na RTX 5050 (`backend/scripts/check_cuda.py`).
2. **Download e cache do áudio** com o `yt-dlp` (`app/download.py`).
3. **Transcrição** com o `faster-whisper` medium/float16 num subprocesso, com cache por `video_id` (`app/transcribe.py`).
4. **Extração de PDF, DOCX e TXT** (`app/extract.py`).
5. **Geração com o Ollama `qwen3:8b`** (`app/llm.py`):
   - JSON validado (schema v2): guia, flashcards (o verso traz só o significado), questões com `difficulty` (`facil`, `medio` ou `dificil`) e subtópicos;
   - **equilíbrio por nível:** o prompt pede exatamente `n_q/3` questões de cada nível, com `n_q` entre 6 e 12, sempre múltiplo de 3;
   - se sair desequilibrado, ele tenta de novo (até 3 tentativas), e `_balance` corta o excesso;
   - as alternativas são embaralhadas (`_shuffle_options`).
6. **Banco e progresso** (`app/db.py`):
   - os subtópicos são unificados por assunto;
   - guarda as tentativas e as revisões, com a data da próxima;
   - guarda a última posição do aluno no assunto.
7. **API FastAPI** com todos os endpoints do plano (alunos, matérias, assuntos, fontes, guia, flashcards, questões, respostas, revisões e progresso), mais `POST /api/sources/{id}/retry`, que regera a fonte reaproveitando a transcrição em cache.
8. **Worker único em fila:** as fontes que ficaram pela metade são retomadas quando o servidor reinicia.
9. **Frontend completo:**
   - escolha de perfil;
   - tela inicial com "Continuar";
   - adicionar conteúdo, com o status ao vivo;
   - página do assunto com três abas: Guia, Flashcards (o card vira; botões "Errei", "Difícil" e "Acertei") e Estudo inteligente (filtros por nível e por subtópico, uma questão por vez com feedback).
10. **Ajustes de design** (commit `dd59e0f`): a fonte nova passou a ter um contorno fino em vez da barra lateral.
11. **Equilíbrio das questões** (commit `3dd0a4b`): as 6 fontes existentes foram regeradas e todas ficaram equilibradas.

**Versões fixadas** (motivos no README):
- `ctranslate2 4.8.5`, `nvidia-cublas-cu12 12.9.2.10` e `nvidia-cudnn-cu12 9.28.1.4`, porque no **Windows** não havia pacote mais novo;
- `av 15.1.0`, porque a versão 16 quebra o `faster-whisper 1.2.1`;
- `OLLAMA_CTX = 8192`, porque com 16k, 20% do modelo vai para a CPU no Windows.

## 4. Migração para o Linux (PRÓXIMO PASSO)
O código é quase todo portátil: usa `pathlib`, `sys.executable` e `nvidia-smi`. O que falta:

1. **`backend/app/gpu.py` → `load_cuda_dlls()`.** Hoje ela só registra as pastas `nvidia/*/bin`, que é o formato do Windows. No Linux as bibliotecas ficam em `nvidia/*/lib`, e o CTranslate2 precisa delas para achar o `libcublas.so.12` e o `libcudnn*.so`. Há duas saídas:
   - exportar `LD_LIBRARY_PATH` com essas pastas **antes** de o processo iniciar, já que a variável é lida na inicialização (por exemplo, no `env` do subprocesso em `transcribe.py`, ou num script de start);
   - carregar com `ctypes.CDLL(..., RTLD_GLOBAL)`.

   Além disso, `os.add_dll_directory` não existe no Linux: a chamada precisa ficar protegida por `os.name == "nt"`.
2. **Versões fixadas em `pyproject.toml`.**
   - As travas do cuBLAS e do cuDNN existem só por causa do Windows. No Linux, use as versões mais novas que funcionem e mantenha o Windows com as travas atuais, se for o caso, usando marcadores `sys_platform`.
   - Confirme que o `ctranslate2` instalado suporta `sm_120`.
3. **Retestar o `OLLAMA_CTX`.** Sem a VRAM que o Windows reserva, talvez 16k caiba inteiro na GPU. Meça com `ollama ps` e o tempo de geração.
4. **Pré-requisitos do sistema:**
   - driver NVIDIA 570 ou mais novo (versão "open"), necessário para a RTX 50;
   - `ffmpeg`, `uv`, Node e Ollama, com `ollama pull qwen3:8b`.
5. **Dados:** copiar a pasta `data/` do Windows (banco, transcrições e áudios). Ela fica fora do git.
6. **Validar:**
   - `uv sync`;
   - `uv run backend/scripts/check_cuda.py`;
   - `uv run backend/scripts/test_transcribe.py <url>`;
   - depois, rodar a API e testar uma fonte de ponta a ponta.
7. **Atualizar o README:** instruções para Linux e revisão dos comentários que citam o Windows (`transcribe.py`, `gpu.py`).

## 5. Pontos a melhorar
**Qualidade da transcrição.** O português sai fluente, mas a ferramenta erra termos técnicos. Exemplos:
- "alfom 4" no lugar de "alfa 1,4";
- "lítio citoplasmático" no lugar de "líquido citoplasmático".

Alguns vídeos também saem quase sem pontuação. Há três caminhos, do mais barato ao mais caro:
1. **`initial_prompt` no Whisper**, com o título do vídeo e o nome da matéria e do assunto. É o caminho **recomendado e ainda não implementado**.
2. **Gravar o `avg_logprob` por segmento** no cache, para medir a confiança e achar os trechos ruins.
3. **`large-v3` em `int8_float16`.** Só vale se o 1 não bastar. No Linux sobra mais VRAM para ele.

**Outros pontos:**
- **Tentativas e revisões antigas:** perderam o vínculo quando as 6 fontes foram regeradas, porque as questões e os flashcards foram recriados. Avaliar se a regeração deveria preservar o histórico.
- **Gemini e NotebookLM:** o NotebookLM não tem API útil para transcrever. A API do Gemini aceita um link do YouTube e evitaria o bloqueio de IP, mas é um serviço na nuvem, com limites e questões de privacidade. Fica só como fallback opcional, se a pessoa quiser.

## 6. Passos futuros
- [ ] Portar para o Linux (seção 4).
- [ ] `initial_prompt` no Whisper com o contexto da fonte.
- [ ] Gravar o `avg_logprob` e exibir os trechos de baixa confiança.
- [ ] Testar o `large-v3` em `int8_float16` e o `OLLAMA_CTX` de 16k no Linux.
- [ ] Preservar o progresso ao regerar uma fonte.
- [ ] (Opcional) Fallback de transcrição pela API do Gemini.

## 7. Como o usuário gosta de trabalhar
- Respostas em português, diretas.
- Não rodar o Whisper e a IA ao mesmo tempo, nunca.
- Mesma experiência no celular e no PC.
- Nome do app: **Acamp**. Contexto de uso: faculdade.
