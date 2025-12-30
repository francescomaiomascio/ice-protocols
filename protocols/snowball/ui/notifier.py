"""
Snowball Host UI

In v1 this is intentionally minimal:
- popup approval
- background notification
"""

def request_user_approval(hostname: str, ip: str, fingerprint: str) -> bool:
    print("\n=== ICE STUDIO — PAIRING REQUEST ===")
    print(f"Host: {hostname}")
    print(f"IP: {ip}")
    print(f"Fingerprint: {fingerprint}")
    print("Approve connection? [y/N]")
    resp = input("> ").strip().lower()
    return resp == "y"
