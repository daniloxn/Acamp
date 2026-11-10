# Acamp — app de estudo

Recebe vídeos do YouTube, PDFs, DOCX e TXT e gera material de estudo com uma IA local, guardando tudo em SQLite, organizado por aluno → matéria → assunto → fontes.

**Vídeo:** `yt-dlp` (áudio original) → `faster-whisper` medium/float16 na GPU → texto
**Documento:** `pymupdf` / `python-docx` → texto

Os dois caminhos depois seguem para o **Ollama `qwen3:8b`**, que gera JSON validado com Pydantic, e terminam em `data/estudo.db`, com backup em `data/study/source_{id}.json`.

Whisper e LLM rodam **estritamente em sequência**:
- a transcrição roda em subprocesso e libera a VRAM ao sair;
- o Ollama usa `keep_alive=0`;
- o pipeline confere a VRAM entre as etapas.

## Conteúdo gerado (schema v2)
- **Guia de estudo:** visão geral, mais seções com resumo e pontos principais.
- **Flashcards:** frente = termo, verso = só o significado.
- **Estudo inteligente:** questões com `difficulty` (`facil`/`medio`/`dificil`) e subtópico, que podem ser filtradas por nível e por tópico.
- **Subtópicos:** pertencem ao assunto e são unificados entre todas as fontes dele.

## Progresso (banco)
- Tentativas de questões, incluindo quais o aluno errou.
- Revisões de flashcards, com a data da próxima revisão.
- Última posição do aluno em cada assunto, para ele continuar de onde parou.

## Rodar o app
```bash
ollama serve                         # em outro terminal
cd frontend && npm install && npm run build && cd ..
cd backend && uv run uvicorn app.api:app --host 0.0.0.0 --port 8000
```
Depois é só abrir http://localhost:8000. Para usar pelo celular na mesma rede, abra `http://<ip-do-pc>:8000`.

**Desenvolvimento do frontend:** com a API rodando, use `cd frontend && npm run dev` e abra http://localhost:5173 (o `/api` é redirecionado por proxy).

A API tem um worker único em fila: as fontes são processadas uma por vez, e o que ficou pela metade é retomado quando o servidor reinicia.

## Comandos
```bash
uv sync
uv run backend/scripts/check_cuda.py              # valida a GPU
uv run backend/scripts/test_download.py <url>     # baixa o áudio (com cache)
uv run backend/scripts/test_transcribe.py <url>   # transcreve e mede a VRAM
uv run backend/scripts/export_schema.py           # gera backend/schema/*.schema.json
uv run backend/scripts/seed_and_run.py            # teste ponta a ponta: banco + vídeo + PDF + filtros + progresso
cd backend && uv run python -m app.pipeline <source_id>
```

Pré-requisito: o Ollama precisa estar rodando (`ollama serve`) com o modelo `qwen3:8b` baixado.

## Versões fixadas (não atualizar sem testar)
- **`ctranslate2 4.8.5`, `nvidia-cublas-cu12 12.9.2.10`, `nvidia-cudnn-cu12 9.28.1.4`:** as versões mais novas do cuBLAS não têm wheel para Windows.
- **`av 15.1.0`:** a versão 16 ou mais nova quebra o `faster-whisper 1.2.1`.
- **`OLLAMA_CTX = 8192`:** com 16k, 20% do modelo vai para a CPU, e a geração fica cerca de 4x mais lenta.
