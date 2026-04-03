from dataclasses import dataclass

@dataclass
class Metrics:
    requests_total: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors_total: int = 0
    last_latency_ms: int = 0

    stable_requests:int=0
    canary_requests:int=0
    stable_errors:int=0
    canary_errors:int=0

METRICS = Metrics()