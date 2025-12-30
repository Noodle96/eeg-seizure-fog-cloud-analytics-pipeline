"""
thresholds.py

Lógica de decisión para determinar si una ventana EEG es sospechosa.

Responsabilidades:
- Cargar umbrales desde configuración (thresholds.yaml)
- Evaluar scores probabilísticos
- Devolver una decisión booleana (True / False)

NO realiza:
- Inferencia
- Alertas
- Procesamiento de señales
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import yaml


# ============================================================
# Configuration loader
# ============================================================

def load_thresholds(
    config_path: Path = Path("fog/config/thresholds.yaml"),
) -> Dict[str, Any]:
    """
    Load threshold configuration from YAML file.

    Parameters
    ----------
    config_path : Path
        Path to thresholds.yaml.

    Returns
    -------
    Dict[str, Any]
        Parsed threshold configuration.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Threshold config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)

    if "inference" not in cfg or "suspicious_threshold" not in cfg["inference"]:
        raise ValueError("Invalid thresholds.yaml structure")

    return cfg


# ============================================================
# Decision logic
# ============================================================

def is_suspected(
    score: float,
    thresholds_cfg: Dict[str, Any] | None = None,
) -> bool:
    """
    Determine whether a window is considered suspicious.

    Parameters
    ----------
    score : float
        Probabilistic score returned by the inference module (0–1).
    thresholds_cfg : Dict[str, Any] | None, optional
        Threshold configuration dictionary. If None, it is loaded
        automatically from thresholds.yaml.

    Returns
    -------
    bool
        True if the window is suspicious, False otherwise.
    """

    if thresholds_cfg is None:
        thresholds_cfg = load_thresholds()

    threshold: float = float(
        thresholds_cfg["inference"]["suspicious_threshold"]
    )

    return score >= threshold
