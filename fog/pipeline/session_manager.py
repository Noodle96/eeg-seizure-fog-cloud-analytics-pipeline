"""
session_manager.py

Gestión del ciclo de vida de sesiones EEG en el nodo Fog.

Responsabilidades:
- Iniciar sesiones (generar session_id)
- Registrar timestamps de inicio y fin
- Mantener contadores básicos por sesión (ej. ventanas procesadas)
- Finalizar sesiones de forma limpia

Notas:
- Por ahora, el estado es solo en memoria.
- Este módulo es el punto correcto para:
  - persistencia local
  - envío de resumen de sesión a cloud
  - métricas por paciente/sesión
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

    Parameters
    ----------
    room_id : str
        Identifier of the room.
    patient_id : str
        Identifier of the patient.

    Returns
    -------
    session_id : str
        Unique session identifier.
    """

    session_id: str = str(uuid.uuid4())
    start_time: str = datetime.utcnow().isoformat()

    _SESSIONS[session_id] = {
        "room_id": room_id,
        "patient_id": patient_id,
        "start_time": start_time,
        "end_time": "",
        "windows_processed": 0,
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

    Parameters
    ----------
    session_id : str
        Identifier of the session.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    _SESSIONS[session_id]["windows_processed"] += 1


def end_session(
    room_id: str,
    patient_id: str,
    session_id: str,
) -> None:
    """
    End an EEG session.

    Parameters
    ----------
    room_id : str
        Identifier of the room.
    patient_id : str
        Identifier of the patient.
    session_id : str
        Identifier of the session.
    """

    if session_id not in _SESSIONS:
        raise KeyError(f"Session not found: {session_id}")

    end_time: str = datetime.utcnow().isoformat()
    _SESSIONS[session_id]["end_time"] = end_time

    windows_processed: int = int(_SESSIONS[session_id]["windows_processed"])

    print(
        "\n"
        "------------------ SESSION END ------------------\n"
        f" Time (UTC)        : {end_time}\n"
        f" Room              : {room_id}\n"
        f" Patient           : {patient_id}\n"
        f" Session ID        : {session_id}\n"
        f" Windows processed : {windows_processed}\n"
        "-------------------------------------------------\n"
    )
