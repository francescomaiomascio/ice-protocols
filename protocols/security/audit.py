import time


def audit_event(event: str, details: dict | None = None):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = details or {}
    print(f"[SECURITY][{ts}] {event} :: {payload}")