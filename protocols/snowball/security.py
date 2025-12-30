import hashlib


def compute_fingerprint(node_id: str, hostname: str) -> str:
    raw = f"{node_id}:{hostname}".encode()
    return hashlib.sha256(raw).hexdigest()


def verify_fingerprint(expected: str, received: str) -> bool:
    return expected == received
