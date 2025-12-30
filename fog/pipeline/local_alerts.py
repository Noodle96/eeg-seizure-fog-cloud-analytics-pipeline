"""
local_alerts.py

Alertas locales inmediatas en el nodo Fog.

Responsabilidades:
- Emitir una alerta cuando una ventana EEG es considerada sospechosa
- Mantener la latencia mínima (sin depender de cloud)

Notas:
- Por ahora, la alerta se imprime por consola.
- Este módulo es el punto correcto para:
  - sonidos
  - LEDs
  - notificaciones locales
  - colas internas del fog
"""

from __future__ import annotations

from datetime import datetime


def trigger_local_alert(
    room_id: str,
    patient_id: str,
    session_id: str,
    window_index: int,
    score: float,
) -> None:
    """
    Trigger a local alert for a suspicious EEG window.

    Parameters
    ----------
    room_id : str
        Identifier of the room (e.g., 'room_A').
    patient_id : str
        Identifier of the patient.
    session_id : str
        Current session identifier.
    window_index : int
        Index of the window within the session.
    score : float
        Probabilistic score that triggered the alert.
    """

    timestamp: str = datetime.utcnow().isoformat()

    # print(
    #     "\n"
    #     "================= LOCAL ALERT =================\n"
    #     f" Time (UTC)   : {timestamp}\n"
    #     f" Room         : {room_id}\n"
    #     f" Patient      : {patient_id}\n"
    #     f" Session      : {session_id}\n"
    #     f" Window index : {window_index}\n"
    #     f" Score        : {score:.4f}\n"
    #     "================================================\n"
    # )
    print("\t\t[ALERT - LOCAL GENERATED]")
