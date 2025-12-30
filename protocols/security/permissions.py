from dataclasses import dataclass


@dataclass
class ResourcePolicy:
    allow_llm: bool = False
    allow_embeddings: bool = False
    allow_backend: bool = False
    max_cpu_percent: int = 100
    max_ram_mb: int | None = None
    max_gpu_layers: int | None = None


def default_local_policy() -> ResourcePolicy:
    return ResourcePolicy(
        allow_llm=True,
        allow_embeddings=True,
        allow_backend=True,
        max_cpu_percent=100,
    )