from pathlib import Path
from typing import Final
import boto3

# ============================================================
# Constants (Fog-side, simple por ahora)
# ============================================================

EDF_BUCKET_NAME: Final[str] = "eeg-seizure-data-lake"
AWS_REGION: Final[str] = "us-east-1"

# ============================================================
# AWS client
# ============================================================

s3_client = boto3.client("s3", region_name=AWS_REGION)


def upload_edf(
    edf_path: Path,
    patient_id: str,
    session_id: str,
) -> None:
    """
    Upload a full EDF file to S3 when session qualifies.

    Parameters
    ----------
    edf_path : Path
        Path to the EDF file.
    patient_id : str
        Patient identifier.
    session_id : str
        Session identifier.
    """

    if not edf_path.exists():
        raise FileNotFoundError(f"EDF file not found: {edf_path}")

    s3_key: str = (
        f"edf/"
        f"patient={patient_id}/"
        f"session={session_id}/"
        f"{edf_path.name}"
    )

    s3_client.upload_file(
        Filename=str(edf_path),
        Bucket=EDF_BUCKET_NAME,
        Key=s3_key,
    )

    print(
        f"[EDF UPLOAD] Uploaded EDF to "
        f"s3://{EDF_BUCKET_NAME}/{s3_key}"
    )
