import json
import queue
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock


_subscribers: dict[int, set[queue.Queue[dict]]] = defaultdict(set)
_lock = Lock()


@contextmanager
def subscribe(task_id: int):
    events: queue.Queue[dict] = queue.Queue()
    with _lock:
        _subscribers[task_id].add(events)
    try:
        yield events
    finally:
        with _lock:
            subscribers = _subscribers.get(task_id)
            if subscribers is not None:
                subscribers.discard(events)
                if not subscribers:
                    _subscribers.pop(task_id, None)


def publish(task_id: int, event: dict) -> None:
    with _lock:
        subscribers = tuple(_subscribers.get(task_id, ()))
    for events in subscribers:
        events.put_nowait(event)


def encode_event(event: dict) -> bytes:
    return f"data: {json.dumps(event, separators=(',', ':'))}\n\n".encode()
