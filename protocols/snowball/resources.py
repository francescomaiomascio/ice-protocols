import platform
from .models import ResourceRequest, ResourceGrant
import time


class ResourceController:
    def verify_local_capabilities(self) -> dict:
        system = platform.system().lower()
        return {
            "os": system,
            "supports_gpu": system == "linux",
            "supports_cgroups": system == "linux",
        }

    def grant(self, request: ResourceRequest) -> ResourceGrant:
        # Qui in v1 si assume che il controllo effettivo
        # venga applicato dal sandbox runtime
        return ResourceGrant(
            cpu_percent=request.cpu_percent,
            ram_mb=request.ram_mb,
            gpu_layers=request.gpu_layers,
            granted_at=time.time(),
        )
