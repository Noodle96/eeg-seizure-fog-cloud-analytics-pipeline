"""
windowing.py

Segmentación temporal de señales EEG en ventanas fijas.

Responsabilidades:
- Recibir señal EEG completa (C, N)
- Generar ventanas contiguas (o solapadas) de duración fija
- (Opcional) simular tiempo real respetando la duración de la ventana

NO realiza:
- Filtrado
- Resampling
- Inferencia
"""

from __future__ import annotations

import time
from typing import Iterator

import numpy as np


def generate_windows(
    signal: np.ndarray,
    sfreq: int,
    window_seconds: float = 4.0,
    overlap_seconds: float = 0.0,
    realtime: bool = True,
) -> Iterator[np.ndarray]:
    """
    Generate EEG windows from a full-length signal.

    Parameters
    ----------
    signal : np.ndarray
        EEG signal of shape (n_channels, n_samples).
    sfreq : int
        Sampling frequency in Hz (e.g., 250).
    window_seconds : float, optional
        Duration of each window in seconds (default: 4.0).
    overlap_seconds : float, optional
        Overlap between consecutive windows in seconds (default: 0.0).
    realtime : bool, optional
        If True, sleeps to simulate real-time streaming.

    Yields
    ------
    window : np.ndarray
        EEG window of shape (n_channels, window_samples).
    """

    if signal.ndim != 2:
        raise ValueError("Signal must have shape (n_channels, n_samples)")

    n_channels, n_samples = signal.shape

    window_samples: int = int(window_seconds * sfreq)
    overlap_samples: int = int(overlap_seconds * sfreq)
    step_samples: int = window_samples - overlap_samples

    if step_samples <= 0:
        raise ValueError("Overlap must be smaller than window duration")

    start: int = 0

    while start + window_samples <= n_samples:
        window: np.ndarray = signal[:, start:start + window_samples]

        yield window

        if realtime:
            time.sleep(window_seconds)

        start += step_samples
