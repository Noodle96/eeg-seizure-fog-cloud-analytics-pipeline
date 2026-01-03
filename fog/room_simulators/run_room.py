#!/usr/bin/env python3
"""
run_room.py

Entrypoint para simular un cuarto (room) dentro del nodo Fog.

Responsabilidades:
- Leer la configuración de asignación de pacientes a cuartos (YAML)
- Seleccionar un cuarto específico (room_A, room_B, etc.)
- Procesar secuencialmente a los pacientes asignados a ese cuarto
- Para cada paciente:
    - Iniciar una sesión
    - Leer su archivo EDF
    - Generar ventanas de EEG (delegado al pipeline)
    - Ejecutar inferencia (mock)
    - Disparar alertas locales inmediatas si corresponde
    - Finalizar la sesión

Este script NO interactúa con la nube.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any

import yaml

# =========================
# Pipeline imports
# =========================
from fog.pipeline.ingestion import load_edf_signal
from fog.pipeline.windowing import generate_windows
from fog.pipeline.inference import run_inference
from fog.pipeline.thresholds import is_suspected
from fog.pipeline.local_alerts import trigger_local_alert
from fog.pipeline.session_manager import (
    start_session,
    end_session,
    register_window,
    register_suspicious_window,
    should_upload_edf,
)
from fog.pipeline.event_builder import build_window_event
from fog.pipeline.edf_uploader import upload_edf
from fog.pipeline.cloud_publisher import publish_event

# =========================
# Types
# =========================

RoomConfig = Dict[str, Any]
PatientConfig = Dict[str, str]


# =========================
# Configuration loader
# =========================

def load_room_assignments(config_path: Path) -> RoomConfig:
    """
    Load room-to-patient assignments from a YAML configuration file.

    Parameters
    ----------
    config_path : Path
        Path to the room_assignments.yaml file.

    Returns
    -------
    RoomConfig
        Parsed YAML content as a dictionary.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        config: RoomConfig = yaml.safe_load(f)

    if "rooms" not in config:
        raise ValueError("Invalid configuration: missing 'rooms' key")

    return config


def load_session_policy(config_path: Path) -> Dict[str, Any]:
    """
    Load session policy configuration from YAML.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Session policy file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        policy: Dict[str, Any] = yaml.safe_load(f)

    if "session" not in policy or "min_suspicious_windows" not in policy["session"]:
        raise ValueError("Invalid session_policy.yaml structure")

    return policy


# =========================
# Room simulation
# =========================
# MIN_SUSPICIOUS_WINDOWS: int = 5  # luego vendrá de YAML
def run_room(room_id: str, config: RoomConfig, session_policy: Dict[str, Any],) -> None:
    """
    Simulate a single room in the Fog node.

    Parameters
    ----------
    room_id : str
        Identifier of the room to simulate (e.g., 'room_A').
    config : RoomConfig
        Parsed configuration containing room assignments.
    """
    rooms: Dict[str, Any] = config["rooms"]

    if room_id not in rooms:
        raise ValueError(f"Room '{room_id}' not found in configuration")

    patients: List[PatientConfig] = rooms[room_id]["patients"]

    print(f"\n[INFO] Starting simulation for room: {room_id}")
    print(f"[INFO] Number of patients assigned: {len(patients)}")

    for patient in patients:
        patient_id: str = patient["patient_id"]
        edf_path: Path = Path(patient["edf_path"])

        print("\n" + "=" * 60)
        print(f"[INFO] Starting session for patient {patient_id} in {room_id}")
        print(f"[INFO] EDF file: {edf_path}")

        # -------------------------
        # Start session
        # -------------------------
        session_id: str = start_session(
            room_id=room_id,
            patient_id=patient_id
        )

        # -------------------------
        # Load EEG signal from EDF
        # -------------------------
        signal, sfreq = load_edf_signal(edf_path)
        print(f"[INFO] EDF signal loaded (sfreq={sfreq} Hz)")
        print(f"[INFO] Signal shape: {signal.shape}")

        # -------------------------
        # Generate and process windows
        # -------------------------
        for window_index, window_data in enumerate(
            generate_windows(signal, sfreq)
        ):
            # print("window_index:", window_index)
            # print("window_data.shape:", window_data.shape)
            print(f"\n\t[INFO] Processing window {window_index} of shape {window_data.shape}")
            # 1️⃣ Registrar ventana procesada
            register_window(session_id)

            # Run inference (mock model)
            probability: float = run_inference(window_data)
            print(f"\t[INFO] Inference probability: {probability:.4f}")

            # Decision logic
            if is_suspected(probability):
                # 1️⃣ Registrar ventana sospechosa
                register_suspicious_window(session_id)

                trigger_local_alert(
                    room_id=room_id,
                    patient_id=patient_id,
                    session_id=session_id,
                    window_index=window_index,
                    score=probability,
                )

            # 2) Construir evento estructurado
            event: dict = build_window_event(
                room_id=room_id,
                patient_id=patient_id,
                session_id=session_id,
                window_index=window_index,
                score=probability,
                suspected=is_suspected(probability),
            )
            publish_event(event)

        # -------------------------
        # End session
        # -------------------------
        end_session(
            room_id=room_id,
            patient_id=patient_id,
            session_id=session_id,
        )
        min_suspicious_windows: int = int(
            session_policy["session"]["min_suspicious_windows"]
        )
        if should_upload_edf(session_id, min_suspicious_windows):
            print(
                f"[INFO] Session {session_id} qualifies for EDF upload "
                f"(>= {min_suspicious_windows} suspicious windows)"
            )
            # upload_edf(edf_path)
            upload_edf( 
                edf_path=edf_path,
                patient_id=patient_id,
                session_id=session_id,
            )
        else:
            print(
                f"[INFO] Session {session_id} does NOT qualify for EDF upload"
            )
        print(f"[INFO] Session finished for patient {patient_id}")

    print(f"\n[INFO] Simulation finished for room: {room_id}")


# =========================
# CLI
# =========================

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Simulate a Fog room processing EEG patients"
    )

    parser.add_argument(
        "--room",
        type=str,
        required=True,
        help="Room identifier to simulate (e.g., room_A, room_B)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("fog/config/room_assignments.yaml"),
        help="Path to room assignments YAML file",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entrypoint.
    """
    args = parse_args()

    try:
        config: RoomConfig = load_room_assignments(args.config)
        session_policy: Dict[str, Any] = load_session_policy(
            Path("fog/config/session_policy.yaml")
        )
        run_room(
            room_id=args.room,
            config=config,
            session_policy=session_policy,
        )
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
