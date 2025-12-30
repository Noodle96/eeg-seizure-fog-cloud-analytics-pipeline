"""
ingestion.py

Carga y preprocesamiento de señales EEG desde archivos EDF.

Responsabilidades:
- Cargar archivo EDF con MNE
- Extraer canales derivados mediante montajes predefinidos
- Aplicar filtrado bandpass + notch
- Remuestrear la señal a una frecuencia objetivo
- Devolver la señal completa lista para windowing

Salida estándar:
- X : np.ndarray con shape (n_channels, n_samples)
- sfreq : int (frecuencia de muestreo final)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import numpy as np
import mne
from scipy.signal import butter, filtfilt, resample, iirnotch, lfilter


# ============================================================
# Configuration constants (fog-level)
# ============================================================

LOWCUT: float = 0.5
HIGHCUT: float = 120.0
FILTER_ORDER: int = 3
TARGET_FS: int = 250


# ============================================================
# Channel extraction
# ============================================================

def get_channels_from_raw(
    raw: mne.io.BaseRaw,
) -> Tuple[bool, np.ndarray]:
    """
    Extract derived EEG channels by subtracting two predefined montages.

    Returns
    -------
    flag_wrong : bool
        True if channel extraction failed.
    signals : np.ndarray
        Shape (n_channels, n_samples)
    """

    montage_list_1 = [
        "EEG FP1-REF", "EEG F7-REF", "EEG T3-REF", "EEG T5-REF",
        "EEG FP2-REF", "EEG F8-REF", "EEG T4-REF", "EEG T6-REF",
        "EEG A1-REF", "EEG T3-REF", "EEG C3-REF", "EEG CZ-REF",
        "EEG C4-REF", "EEG T4-REF", "EEG FP1-REF", "EEG F3-REF",
        "EEG C3-REF", "EEG P3-REF", "EEG FP2-REF", "EEG F4-REF",
        "EEG C4-REF", "EEG P4-REF",
    ]

    montage_list_2 = [
        "EEG F7-REF", "EEG T3-REF", "EEG T5-REF", "EEG O1-REF",
        "EEG F8-REF", "EEG T4-REF", "EEG T6-REF", "EEG O2-REF",
        "EEG T3-REF", "EEG C3-REF", "EEG CZ-REF", "EEG C4-REF",
        "EEG T4-REF", "EEG A2-REF", "EEG F3-REF", "EEG C3-REF",
        "EEG P3-REF", "EEG O1-REF", "EEG F4-REF", "EEG C4-REF",
        "EEG P4-REF", "EEG O2-REF",
    ]

    try:
        idx1 = [raw.ch_names.index(ch) for ch in montage_list_1]
        idx2 = [raw.ch_names.index(ch) for ch in montage_list_2]

        sig1 = raw.get_data(picks=idx1)
        sig2 = raw.get_data(picks=idx2)

    except Exception:
        return True, np.empty((0, 0))

    signals = sig1 - sig2
    return False, signals


# ============================================================
# Filtering helpers
# ============================================================

def butter_bandpass(
    lowcut: float,
    highcut: float,
    fs: float,
    order: int,
) -> Tuple[np.ndarray, np.ndarray]:
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    return butter(order, [low, high], btype="band")


def butter_bandpass_filter(
    data: np.ndarray,
    fs: float,
) -> np.ndarray:
    b, a = butter_bandpass(LOWCUT, HIGHCUT, fs, FILTER_ORDER)
    return filtfilt(b, a, data)


# ============================================================
# Resampling
# ============================================================

def resample_data_in_each_channel(
    signals: List[np.ndarray],
    original_fs: int,
    target_fs: int,
) -> List[np.ndarray]:
    resampled: List[np.ndarray] = []

    for sig in signals:
        n_samples = int(len(sig) / original_fs * target_fs)
        resampled.append(resample(sig, n_samples))

    return resampled


# ============================================================
# Main ingestion function
# ============================================================

def load_edf_signal(
    edf_path: Path,
) -> Tuple[np.ndarray, int]:
    """
    Load and preprocess an EDF file.

    Parameters
    ----------
    edf_path : Path
        Path to EDF file.

    Returns
    -------
    X : np.ndarray
        EEG signal with shape (n_channels, n_samples)
    sfreq : int
        Final sampling frequency (TARGET_FS)
    """

    raw = mne.io.read_raw_edf(
        edf_path,
        preload=True,
        verbose="warning",
    )

    original_fs: int = int(raw.info["sfreq"])

    flag_wrong, signals = get_channels_from_raw(raw)
    if flag_wrong:
        raise RuntimeError("Channel extraction failed")

    # Bandpass + notch filtering (signal-wise)
    notch_1_b, notch_1_a = iirnotch(1.0, Q=30.0, fs=TARGET_FS)
    notch_60_b, notch_60_a = iirnotch(60.0, Q=30.0, fs=TARGET_FS)

    filtered: List[np.ndarray] = []

    for ch in signals:
        band = butter_bandpass_filter(ch, original_fs)
        notch1 = lfilter(notch_1_b, notch_1_a, band)
        notch60 = lfilter(notch_60_b, notch_60_a, notch1)
        filtered.append(notch60)

    # Resampling
    if original_fs != TARGET_FS:
        filtered = resample_data_in_each_channel(
            filtered,
            original_fs,
            TARGET_FS,
        )

    X = np.stack(filtered)
    return X, TARGET_FS
