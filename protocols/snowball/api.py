from __future__ import annotations
# src/ice_studio/snowball/api.py

from dataclasses import asdict
from typing import Dict, Any

from .agent import SnowballAgent
from .models import SnowballRequest
from .state import SnowballState


class SnowballAPI:
    """
    API ufficiale Snowball.
    Usata da:
    - Preboot
    - APA
    - future automazioni
    """

    def __init__(self, agent: SnowballAgent):
        self.agent = agent

    def discover(self) -> list[dict]:
        return self.agent.discover_hosts()

    def request_pairing(self, payload: Dict[str, Any]) -> dict:
        req = SnowballRequest(**payload)
        result = self.agent.create_pairing(req)
        return asdict(result)

    def approve_pairing(self, request_id: str) -> bool:
        return self.agent.approve_pairing(request_id)

    def status(self) -> dict:
        return {
            "state": self.agent.state.name,
            "paired": self.agent.state == SnowballState.PAIRED,
            "trusted": self.agent.list_trusted_hosts(),
        }

    def grant_resources(self, grant: dict) -> bool:
        return self.agent.apply_resource_grant(grant)
