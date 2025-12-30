"""
inference.py

Inferencia (mock) sobre ventanas EEG.

Responsabilidades:
- Recibir una ventana EEG (C, T)
- Devolver un score probabilístico en [0, 1]

Notas:
- Este módulo NO implementa un modelo real.
- El objetivo es simular el comportamiento de un modelo
  hasta integrar uno entrenado más adelante.
"""

from __future__ import annotations

from typing import Optional
import numpy as np


def run_inference(
    window: np.ndarray,
    seed: Optional[int] = None,
) -> float:
    """
    Run mock inference on a single EEG window.

    Parameters
    ----------
    window : np.ndarray
        EEG window with shape (n_channels, n_samples).
    seed : Optional[int], optional
        Random seed for reproducibility (default: None).

    Returns
    -------
    score : float
        Probabilistic score in the range [0, 1].
    """

    if window.ndim != 2:
        raise ValueError("Window must have shape (n_channels, n_samples)")

    if seed is not None:
        np.random.seed(seed)

    # --------------------------------------------------
    # Mock behavior:
    # - Use simple statistics to make the score depend
    #   on the signal (not purely random)
    # --------------------------------------------------

    # Energy-based heuristic (very rough)
    energy: float = float(np.mean(window ** 2))

    # Normalize energy to a pseudo-probability
    # (these constants are arbitrary for simulation)
    normalized_energy: float = min(energy / 100.0, 1.0)

    # Add controlled randomness
    noise: float = float(np.random.uniform(0.0, 0.1))

    score: float = min(max(normalized_energy + noise, 0.0), 1.0)

    return score
