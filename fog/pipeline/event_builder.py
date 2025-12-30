"""
event_builder.py

Construcción de eventos estructurados a partir de hechos ocurridos en el fog.

Responsabilidades:
- Crear un diccionario JSON-ready que describa un evento EEG
- Mantener un esquema estable y versionable
- Desacoplar el fog de la capa cloud

NO realiza:
- Inferencia
- Decisiones
- Alertas
- Envío a la nube
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any


def build_suspected_window_event(
    room_id: str,
    patient_id: str,
    session_id: str,
    window_index: int,
    score: float,
) -> Dict[str, Any]:
    """
    Build an event for a suspected EEG window.

    Parameters
    ----------
    room_id : str
        Identifier of the room (e.g., 'room_A').
    patient_id : str
        Identifier of the patient.
    session_id : str
        Identifier of the EEG session.
    window_index : int
        Index of the window within the session.
    score : float
        Probabilistic score associated with the window.

    Returns
    -------
    Dict[str, Any]
        JSON-serializable event dictionary.
    """

    event: Dict[str, Any] = {
        "event_version": "1.0",
        "event_type": "SUSPECTED_EEG_WINDOW",
        "timestamp_utc": datetime.utcnow().isoformat(),

        # Context
        "room_id": room_id,
        "patient_id": patient_id,
        "session_id": session_id,

        # Window-level info
        "window_index": window_index,
        "score": float(score),
    }

    return event
