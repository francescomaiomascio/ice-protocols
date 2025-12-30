from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

TRUSTED_DIR = Path.home() / ".ice_studio"
TRUSTED_HOSTS_PATH = TRUSTED_DIR / "trusted_hosts.json"
TRUSTED_CLIENTS_PATH = TRUSTED_DIR / "trusted_clients.json"


@dataclass
class PairingRequest:
    request_id: str

    # host info (remote flake)
    host_id: str
    host_hostname: str
    host_ip: str

    # client info (questa macchina preboot)
    client_id: str
    client_fingerprint: str

    created_at: float
    approved: bool = False


@dataclass
class TrustedHost:
    host_id: str
    hostname: str
    ip: str
    fingerprint: str
    paired_at: float


@dataclass
class TrustedClient:
    client_id: str
    fingerprint: str
    paired_at: float


_PAIRINGS: Dict[str, PairingRequest] = {}
_TRUSTED_HOSTS: Dict[str, TrustedHost] = {}
_TRUSTED_CLIENTS: Dict[str, TrustedClient] = {}
_SELECTED_HOST_ID: Optional[str] = None

logger = logging.getLogger("ice.preboot")


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def _ensure_dir() -> None:
    TRUSTED_DIR.mkdir(parents=True, exist_ok=True)


def _load_trusted_hosts() -> None:
    if not TRUSTED_HOSTS_PATH.exists():
        return
    try:
        data = json.loads(TRUSTED_HOSTS_PATH.read_text())
    except Exception:
        return

    for entry in data:
        try:
            host = TrustedHost(**entry)
            _TRUSTED_HOSTS[host.host_id] = host
        except TypeError:
            continue


def _save_trusted_hosts() -> None:
    _ensure_dir()
    data = [asdict(host) for host in _TRUSTED_HOSTS.values()]
    TRUSTED_HOSTS_PATH.write_text(json.dumps(data, indent=2))


def _load_trusted_clients() -> None:
    if not TRUSTED_CLIENTS_PATH.exists():
        return
    try:
        data = json.loads(TRUSTED_CLIENTS_PATH.read_text())
    except Exception:
        return

    for entry in data:
        try:
            client = TrustedClient(**entry)
            _TRUSTED_CLIENTS[client.client_id] = client
        except TypeError:
            continue


def _save_trusted_clients() -> None:
    _ensure_dir()
    data = [asdict(client) for client in _TRUSTED_CLIENTS.values()]
    TRUSTED_CLIENTS_PATH.write_text(json.dumps(data, indent=2))


# Carica subito host/client già trusted
_load_trusted_hosts()
_load_trusted_clients()


# ---------------------------------------------------------------------------
# Pairing lifecycle
# ---------------------------------------------------------------------------

def create_pairing_request(payload: dict) -> PairingRequest:
    """
    Crea una richiesta di pairing per un host remoto.

    Payload tipico dalla UI:
      {
        "host_id": "...",
        "ip": "192.168.0.X",
        "hostname": "Exon",
        // opzionali:
        "client_id": "...",
        "client_fingerprint": "...",
      }
    """
    host_id = (
        payload.get("host_id")
        or payload.get("node_id")
        or payload.get("hostname")
        or payload.get("ip")
        or "unknown-host"
    )
    host_hostname = payload.get("hostname") or host_id
    host_ip = payload.get("ip") or payload.get("host_ip") or ""

    client_id = payload.get("client_id") or payload.get("node_id") or str(uuid.uuid4())
    fingerprint = (
        payload.get("client_fingerprint")
        or payload.get("fingerprint")
        or ""
    )

    req = PairingRequest(
        request_id=str(uuid.uuid4()),
        host_id=host_id,
        host_hostname=host_hostname,
        host_ip=host_ip,
        client_id=client_id,
        client_fingerprint=fingerprint,
        created_at=time.time(),
        approved=False,
    )
    _PAIRINGS[req.request_id] = req

    logger.info(
        "[PAIRING] request created host_id=%s ip=%s client_id=%s",
        req.host_id,
        req.host_ip,
        req.client_id,
    )
    return req


def list_pairings() -> List[dict]:
    return [asdict(p) for p in _PAIRINGS.values()]


def list_trusted_hosts() -> List[dict]:
    return [asdict(host) for host in _TRUSTED_HOSTS.values()]


def list_trusted_clients() -> List[dict]:
    return [asdict(client) for client in _TRUSTED_CLIENTS.values()]


def trust_host(host_id: str, hostname: str, ip: str, fingerprint: str) -> TrustedHost:
    """
    Aggiunge/aggiorna un host nella lista dei flake trusted.
    """
    existing = _TRUSTED_HOSTS.get(host_id)
    if existing:
        # aggiorna info esistenti
        if hostname:
            existing.hostname = hostname
        if ip:
            existing.ip = ip
        if fingerprint:
            existing.fingerprint = fingerprint
        if not existing.paired_at:
            existing.paired_at = time.time()
        trusted = existing
    else:
        trusted = TrustedHost(
            host_id=host_id,
            hostname=hostname or host_id,
            ip=ip,
            fingerprint=fingerprint or "",
            paired_at=time.time(),
        )
        _TRUSTED_HOSTS[host_id] = trusted

    _save_trusted_hosts()
    logger.info(
        "[SECURITY] trusted host saved host_id=%s hostname=%s ip=%s",
        trusted.host_id,
        trusted.hostname,
        trusted.ip,
    )
    return trusted


def load_trusted_hosts() -> Dict[str, TrustedHost]:
    return dict(_TRUSTED_HOSTS)


def load_trusted_clients() -> Dict[str, TrustedClient]:
    return dict(_TRUSTED_CLIENTS)


def approve_pairing(request_id: str) -> bool:
    """
    Chiamata dal daemon (via /preboot/pairing/approve) quando l'utente
    clicca "Accept flake" sul popup.

    Effetti:
    - segna la PairingRequest come approvata
    - aggiunge/aggiorna TrustedHost
    - registra TrustedClient
    - seleziona l'host come corrente
    """
    req = _PAIRINGS.get(request_id)
    if not req:
        logger.warning("[PAIRING] approve failed: unknown request_id=%s", request_id)
        return False

    if req.approved:
        # già approvata in passato → idempotente
        return True

    req.approved = True

    # Host trusted (flake)
    trusted_host = trust_host(
        host_id=req.host_id,
        hostname=req.host_hostname,
        ip=req.host_ip,
        fingerprint="",  # fingerprint host opzionale, per ora vuoto
    )

    # Client trusted
    trusted_client = TrustedClient(
        client_id=req.client_id,
        fingerprint=req.client_fingerprint,
        paired_at=time.time(),
    )
    _TRUSTED_CLIENTS[trusted_client.client_id] = trusted_client
    _save_trusted_clients()

    # Seleziona l'host come target corrente
    select_host(trusted_host.host_id)

    logger.info(
        "[PAIRING] approved client_id=%s host_id=%s ip=%s",
        trusted_client.client_id,
        trusted_host.host_id,
        trusted_host.ip,
    )
    return True


# ---------------------------------------------------------------------------
# Status / selection
# ---------------------------------------------------------------------------

def pairing_status(host_id: Optional[str]) -> dict:
    """
    Ritorna lo stato di pairing lato preboot per l'host richiesto.
    Usato dal polling JS (/preboot/pairing/status).
    """
    trusted = load_trusted_hosts()
    selected = selected_host()
    is_trusted = bool(host_id and host_id in trusted)

    return {
        "trusted": is_trusted,
        "status": "approved" if is_trusted else "pending",
        "selected_host": selected,
        "trusted_hosts": list_trusted_hosts(),
    }


def select_host(host_id: str) -> bool:
    """
    Marca un host trusted come 'selected' (per SNOWBALL / runtime remote).
    """
    if host_id not in _TRUSTED_HOSTS:
        logger.warning(
            "[PAIRING] select_host ignored: host_id=%s not in trusted", host_id
        )
        return False

    global _SELECTED_HOST_ID
    _SELECTED_HOST_ID = host_id
    logger.info("[PAIRING] selected_host=%s", host_id)
    return True


def selected_host() -> Optional[dict]:
    if not _SELECTED_HOST_ID:
        return None
    host = _TRUSTED_HOSTS.get(_SELECTED_HOST_ID)
    return asdict(host) if host else None
