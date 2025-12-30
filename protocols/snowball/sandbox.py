from __future__ import annotations
# src/ice_studio/snowball/sandbox.py

import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional

from .resources import ResourceGrant
from .security import audit_event


@dataclass
class SandboxHandle:
    pid: int
    cgroup: Optional[str] = None
    namespace: Optional[str] = None


class SandboxManager:
    """
    Sandbox minimale Snowball.
    Linux-first. No Docker. No install.
    """

    def __init__(self) -> None:
        self.platform = platform.system().lower()

    def supported(self) -> bool:
        return self.platform == "linux"

    def launch(
        self,
        command: list[str],
        resources: ResourceGrant,
    ) -> SandboxHandle:
        if not self.supported():
            audit_event(
                "sandbox.unsupported_platform",
                {"platform": self.platform},
            )
            raise RuntimeError("Sandbox supported only on Linux")

        audit_event(
            "sandbox.launch",
            {
                "cpu": resources.cpu_percent,
                "ram": resources.ram_mb,
                "gpu": resources.gpu_layers,
            },
        )

        cmd = self._build_command(command, resources)
        proc = subprocess.Popen(cmd)

        return SandboxHandle(pid=proc.pid)

    def _build_command(
        self,
        command: list[str],
        resources: ResourceGrant,
    ) -> list[str]:
        """
        Usa:
        - cgroups v2 (cpu, memory)
        - nice per fallback
        """
        cmd = []

        if resources.cpu_percent < 100:
            cmd += ["nice", "-n", "10"]

        if resources.ram_mb:
            cmd += [
                "systemd-run",
                "--scope",
                f"-pMemoryMax={resources.ram_mb}M",
            ]

        cmd += command
        return cmd
