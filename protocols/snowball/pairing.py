import time
import uuid
from .models import PairingRequest
from .state import SnowballState
from .security import compute_fingerprint
from .ui.notifier import request_user_approval


class PairingService:
    def __init__(self, state: SnowballState):
        self.state = state

    def handle_pairing(self, node_id: str, hostname: str, ip: str) -> bool:
        fingerprint = compute_fingerprint(node_id, hostname)

        if self.state.is_trusted(node_id):
            return True

        req = PairingRequest(
            request_id=str(uuid.uuid4()),
            node_id=node_id,
            hostname=hostname,
            ip=ip,
            fingerprint=fingerprint,
            created_at=time.time(),
        )

        approved = request_user_approval(hostname, ip, fingerprint)
        if approved:
            req.approved = True
            self.state.trust_host(req)
            return True

        return False
