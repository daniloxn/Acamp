"""Fila simples com UM worker: processa uma fonte por vez (nunca dois jobs na GPU)."""
import queue
import threading
import traceback

from app import db
from app.pipeline import process

_q: "queue.Queue[int]" = queue.Queue()
_queued: set[int] = set()
_lock = threading.Lock()


def enqueue(source_id: int) -> None:
    with _lock:
        if source_id in _queued:
            return
        _queued.add(source_id)
    db.update_source(source_id, status="queued", error=None)
    _q.put(source_id)


def _loop() -> None:
    while True:
        sid = _q.get()
        try:
            if db.get_source(sid):  # pode ter sido apagada enquanto esperava
                process(sid)
        except Exception:
            traceback.print_exc()
        finally:
            with _lock:
                _queued.discard(sid)


def start() -> None:
    threading.Thread(target=_loop, name="gpu-worker", daemon=True).start()
    for src in db.list_sources(pending_only=True):  # retoma o que ficou pela metade
        enqueue(src.id)
