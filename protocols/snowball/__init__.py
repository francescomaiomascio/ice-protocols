"""
Snowball — Host Control Plane for ICE Studio

Snowball is responsible for:
- Pairing & trust establishment
- Resource isolation and policy enforcement
- Minimal host-side UI interaction
- Secure session control for remote runtimes
"""
from .agent import SnowballAgent
from .state import SnowballState
from .models import ResourceGrant, PairingRequest
