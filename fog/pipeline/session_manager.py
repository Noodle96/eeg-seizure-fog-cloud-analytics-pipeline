"""
session_manager.py

Gestión del ciclo de vida de sesiones EEG en el nodo Fog.

Responsabilidades:
- Iniciar sesiones (generar session_id)
- Registrar timestamps de inicio y fin
- Mantener contadores por sesión
  - ventanas procesadas
  - ventanas sospechosas
- Decidir políticas post-sesión (ej. subir EDF o no)

Notas:
- El estado es solo en memoria (correcto para fog).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict
import uuid


# ============================================================
# In-memory session registry
# ============================================================

_SESSIONS: Dict[str, Dict[str, str | int]] = {}


# ============================================================
# Session lifecycle
# ============================================================

def start_session(
    room_id: str,
    patient_id: str,
) -> str:
    """
    Start a new EEG session.
    """

    session_id: str = str(uuid.uuid4())
    start_time: str = datetime.utcnow().isoformat()

    _SESSIONS[session_id] = {
        "room_id": room_id,
        "patient_id": patient_id,
        "start_time": start_time,
        "end_time": "",
        "windows_processed": 0,
        "suspicious_windows": 0,
    }

    print(
        "\n"
        "----------------- SESSION START -----------------\n"
        f" Time (UTC) : {start_time}\n"
        f" Room       : {room_id}\n"
        f" Patient    : {patient_id}\n"
        f" Session ID : {session_id}\n"
        "-------------------------------------------------\n"
    )

    return session_id


def register_window(
    session_id: str,
) -> None:
    """
    Register that a window has been processed in a session.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    _SESSIONS[session_id]["windows_processed"] += 1


def register_suspicious_window(
    session_id: str,
) -> None:
    """
    Register a suspicious window for a session.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    _SESSIONS[session_id]["suspicious_windows"] += 1


def should_upload_edf(
    session_id: str,
    min_suspicious_windows: int,
) -> bool:
    """
    Decide whether the EDF file of a session should be uploaded.

    Parameters
    ----------
    session_id : str
        Identifier of the session.
    min_suspicious_windows : int
        Minimum number of suspicious windows required.

    Returns
    -------
    bool
        True if EDF should be uploaded, False otherwise.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    suspicious_windows: int = int(
        _SESSIONS[session_id]["suspicious_windows"]
    )

    return suspicious_windows >= min_suspicious_windows


def end_session(
    room_id: str,
    patient_id: str,
    session_id: str,
) -> None:
    """
    End an EEG session.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    end_time: str = datetime.utcnow().isoformat()
    _SESSIONS[session_id]["end_time"] = end_time

    windows_processed: int = int(_SESSIONS[session_id]["windows_processed"])
    suspicious_windows: int = int(_SESSIONS[session_id]["suspicious_windows"])

    print(
        "\n"
        "------------------ SESSION END ------------------\n"
        f" Time (UTC)              : {end_time}\n"
        f" Room                    : {room_id}\n"
        f" Patient                 : {patient_id}\n"
        f" Session ID              : {session_id}\n"
        f" Windows processed       : {windows_processed}\n"
        f" Suspicious windows      : {suspicious_windows}\n"
        "-------------------------------------------------\n"
    )
