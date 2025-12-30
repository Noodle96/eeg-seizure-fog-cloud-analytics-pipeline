from __future__ import annotations

import json
from typing import Any, Dict, Final, Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError


# ============================================================
# Constants (explicit, no env vars for now)
# ============================================================

CLOUD_ENABLED: Final[bool] = True

AWS_REGION: Final[str] = "us-east-1"
KINESIS_STREAM_NAME: Final[str] = "eeg-seizure-event-stream"


# ============================================================
# Kinesis Client (lazy initialization)
# ============================================================

_kinesis_client: Optional[BaseClient] = None


def _get_kinesis_client() -> BaseClient:
    """
    Lazily initialize and return a Kinesis client.
    """
    global _kinesis_client

    if _kinesis_client is None:
        _kinesis_client = boto3.client(
            "kinesis",
            region_name=AWS_REGION,
        )

    return _kinesis_client


# ============================================================
# Public API
# ============================================================

def publish_event(event: Dict[str, Any]) -> None:
    """
    Publish a single EEG window event to Kinesis.

    If cloud publishing is disabled, this function is a no-op.
    """

    if not CLOUD_ENABLED:
        return

    client: BaseClient = _get_kinesis_client()

    try:
        payload: bytes = json.dumps(event).encode("utf-8")

        client.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=payload,
            PartitionKey=event.get(
                "partition_key",
                event.get("patient_id", "default"),
            ),
        )

        # print(
        #     f"[KINESIS] Event published | "
        #     f"session={event.get('session_id')} "
        #     f"window={event.get('window_index')}"
        # )
        print(f"\t\t[cloud_publisher] Event published")

    except (BotoCoreError, ClientError) as exc:
        print(f"[KINESIS][ERROR] Failed to publish event: {exc}")
