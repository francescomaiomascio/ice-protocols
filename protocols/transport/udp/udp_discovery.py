from __future__ import annotations

import socket
import json
import threading
import time
from typing import List, Dict

DISCOVERY_PORT = 7042
DISCOVERY_MAGIC = "ICE_DISCOVERY_V2"


def start_udp_responder(identity: Dict):
    """
    Avvia responder UDP ICE.
    Deve partire SEMPRE in preboot e runtime.
    """
    def _run():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", DISCOVERY_PORT))

        while True:
            data, addr = sock.recvfrom(1024)
            try:
                if data.decode() == DISCOVERY_MAGIC:
                    sock.sendto(json.dumps(identity).encode(), addr)
            except Exception:
                continue

    threading.Thread(target=_run, daemon=True).start()


def udp_discovery(timeout: float = 1.2) -> List[Dict]:
    """
    Broadcast UDP per trovare nodi ICE.
    Tempo massimo: timeout (default 1.2s)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    sock.sendto(DISCOVERY_MAGIC.encode(), ("<broadcast>", DISCOVERY_PORT))

    devices = []
    start = time.time()

    while time.time() - start < timeout:
        try:
            data, addr = sock.recvfrom(2048)
            payload = json.loads(data.decode())
            payload["seen_at"] = time.time()
            devices.append(payload)
        except socket.timeout:
            break
        except Exception:
            continue

    return devices
