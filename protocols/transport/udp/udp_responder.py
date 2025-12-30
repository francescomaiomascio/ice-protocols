import json
from engine.logging.router import get_logger
import socket
import threading
import time
from typing import Optional

DISCOVERY_PORT = 7042
DISCOVERY_MAGIC = "ICE_DISCOVERY_V2"
logger = get_logger("icenet", "discovery", "ice.network.udp_responder")


def start_udp_responder(identity: dict | None = None) -> Optional[threading.Thread]:
    """Start a best-effort UDP responder for LAN discovery probes."""

    if not identity:
        logger.warning("UDP responder identity missing; not starting responder")
        return None

    payload = json.dumps(identity).encode("utf-8")

    def _loop():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(("", DISCOVERY_PORT))
        except OSError as err:
            logger.error("UDP responder failed to bind on %s: %s", DISCOVERY_PORT, err)
            return

        logger.info("UDP responder active on port %s", DISCOVERY_PORT)

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if not data:
                    continue
                msg = data.decode("utf-8", errors="ignore").strip()
                if msg == DISCOVERY_MAGIC:
                    sock.sendto(payload, addr)
            except Exception as err:
                logger.warning("UDP responder error: %s", err)
                time.sleep(0.2)

    thread = threading.Thread(target=_loop, name="udp-responder", daemon=True)
    thread.start()
    return thread
