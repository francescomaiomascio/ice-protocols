from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import time


@dataclass(frozen=True)
class ResourceRequest:
    cpu_percent: int
    ram_mb: int
    gpu_layers: Optional[int] = None


@dataclass
class ResourceGrant:
    cpu_percent: int
    ram_mb: int
    gpu_layers: Optional[int]
    granted_at: float


@dataclass
class PairingRequest:
    request_id: str
    node_id: str
    hostname: str
    ip: str
    fingerprint: str
    created_at: float
    approved: bool = False
