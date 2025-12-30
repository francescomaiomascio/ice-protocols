from .state import SnowballState
from .pairing import PairingService
from .resources import ResourceController
from .models import ResourceRequest


class SnowballAgent:
    def __init__(self):
        self.state = SnowballState()
        self.pairing = PairingService(self.state)
        self.resources = ResourceController()

    def accept_connection(
        self,
        node_id: str,
        hostname: str,
        ip: str,
        resource_request: ResourceRequest,
    ):
        if not self.pairing.handle_pairing(node_id, hostname, ip):
            raise PermissionError("Pairing rejected by host")

        capabilities = self.resources.verify_local_capabilities()
        grant = self.resources.grant(resource_request)

        return {
            "trusted": True,
            "capabilities": capabilities,
            "resource_grant": grant,
        }
