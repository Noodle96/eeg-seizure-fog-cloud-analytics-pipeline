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
from pipeline.ingestion import load_edf_signal
from pipeline.windowing import generate_windows
from pipeline.inference import run_inference
from pipeline.thresholds import is_suspected
from pipeline.local_alerts import trigger_local_alert
from pipeline.session_manager import (
    start_session,
    end_session,
)
from pipeline.event_builder import build_suspected_window_event


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


# =========================
# Room simulation
# =========================

def run_room(room_id: str, config: RoomConfig) -> None:
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

        # -------------------------
        # Generate and process windows
        # -------------------------
        for window_index, window_data in enumerate(
            generate_windows(signal, sfreq)
        ):
            # Run inference (mock model)
            probability: float = run_inference(window_data)

            # Decision logic
            if is_suspected(probability):
                trigger_local_alert(
                    room_id=room_id,
                    patient_id=patient_id,
                    session_id=session_id,
                    window_index=window_index,
                    score=probability,
                )

                # 2) Construir evento estructurado
                event: dict = build_suspected_window_event(
                    room_id=room_id,
                    patient_id=patient_id,
                    session_id=session_id,
                    window_index=window_index,
                    score=probability,
                )
                # 3) Por ahora solo lo mostramos (luego va a cloud)
                print("[EVENT BUILT]", event)

        # -------------------------
        # End session
        # -------------------------
        end_session(
            room_id=room_id,
            patient_id=patient_id,
            session_id=session_id,
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
        run_room(args.room, config)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
