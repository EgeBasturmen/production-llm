import hashlib

def choose_variant(request_id: str, canary_percent: int = 10) -> str:
    """
    request_id üzerinden deterministik split:
    - %canary_percent canary
    - kalan stable
    """
    h = hashlib.md5(request_id.encode("utf-8")).hexdigest()
    bucket = int(h[:2], 16)  # 0..255
    pct = (bucket / 255) * 100
    return "canary" if pct < canary_percent else "stable"