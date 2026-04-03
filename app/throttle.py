import time
from threading import Lock

_lock = Lock()
_last_call = 0.0

def throttle(min_interval_sec: float = 2.0) -> None:
    """
    Global (process-wide) simple throttle.
    Ensures at most 1 call per min_interval_sec.
    """
    global _last_call
    with _lock:
        now = time.time()
        wait = (_last_call + min_interval_sec) - now
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()