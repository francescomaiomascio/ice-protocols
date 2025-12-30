# ice_studio/security/identity.py
from dataclasses import dataclass
from enum import Enum
import socket
import uuid

class NodeRole(str, Enum):
    CLIENT = "client"
    HOST = "host"

@dataclass
class NodeIdentity:
    node_id: str
    hostname: str
    ip: str
    role: NodeRole
    fingerprint: str


def get_local_identity(role: NodeRole) -> NodeIdentity:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    node_id = str(uuid.getnode())      # stabile
    fingerprint = f"SHA256:{node_id}"  # placeholder, ok per ora

    return NodeIdentity(
        node_id=node_id,
        hostname=hostname,
        ip=ip,
        role=role,
        fingerprint=fingerprint,
    )
