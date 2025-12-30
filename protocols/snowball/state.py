from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict
from dataclasses import asdict
from .models import PairingRequest


STATE_PATH = Path.home() / ".ice_studio" / "snowball_state.json"


class SnowballState:
    def __init__(self):
        self.pairings: Dict[str, PairingRequest] = {}
        self.trusted_hosts: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if not STATE_PATH.exists():
            return
        try:
            data = json.loads(STATE_PATH.read_text())
            self.trusted_hosts = data.get("trusted_hosts", {})
        except Exception:
            pass

    def save(self):
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps(
                {
                    "trusted_hosts": self.trusted_hosts,
                },
                indent=2,
            )
        )

    def trust_host(self, pairing: PairingRequest):
        self.trusted_hosts[pairing.node_id] = {
            "hostname": pairing.hostname,
            "ip": pairing.ip,
            "fingerprint": pairing.fingerprint,
            "paired_at": time.time(),
        }
        self.save()

    def is_trusted(self, node_id: str) -> bool:
        return node_id in self.trusted_hosts
