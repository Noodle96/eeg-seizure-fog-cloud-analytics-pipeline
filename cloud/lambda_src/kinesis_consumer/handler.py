from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any, Dict, List

import boto3
import os

# ============================================================
# Environment / constants
# ============================================================

RAW_EVENTS_BUCKET = "eeg-seizure-data-lake"
DYNAMO_TABLE_NAME = "eeg-seizure-session-state"

# ============================================================
# AWS clients
# ============================================================

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMO_TABLE_NAME)


# ============================================================
# Helper functions
# ============================================================

def decode_kinesis_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decode a single Kinesis record into a JSON event.
    """
    payload_bytes: bytes = base64.b64decode(record["kinesis"]["data"])
    payload_str: str = payload_bytes.decode("utf-8")
    return json.loads(payload_str)


def store_event_in_s3(event: Dict[str, Any]) -> None:
    print("BEGIN store_event_in_s3")
    """
    Append EEG event to S3 as JSONL.
    """
    date_prefix: str = datetime.utcnow().strftime("%Y/%m/%d")
    key: str = (
        f"events/"
        f"{date_prefix}/"
        f"patient={event['patient_id']}/"
        f"session={event['session_id']}/"
        f"window={event['window_index']}.json"
    )

    s3_client.put_object(
        Bucket=RAW_EVENTS_BUCKET,
        Key=key,
        Body=json.dumps(event) + "\n",
    )
    print(f"[INFO] Stored event in S3: s3://{RAW_EVENTS_BUCKET}/{key}")


def update_dynamodb(event: Dict[str, Any]) -> None:
    print("BEGIN update_dynamodb")
    """
    Update aggregated counters in DynamoDB.
    """
    print(
        "[DEBUG] Dynamo Key:",
        {
            "pk": event["patient_id"],
            "sk": event["session_id"],
        },
    )
    table.update_item(
        Key={
            "pk": event["patient_id"],
            "sk": event["session_id"],
        },
        UpdateExpression="""
            ADD windows_total :one,
                suspected_windows :sus
        """,
        ExpressionAttributeValues={
            ":one": 1,
            ":sus": 1 if event["suspected"] else 0,
        },
    )
    print(f"[INFO] Updated DynamoDB for patient {event['patient_id']}, session {event['session_id']}")


# ============================================================
# Lambda handler
# ============================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Kinesis consumer Lambda.
    """
    records: List[Dict[str, Any]] = event.get("Records", [])

    print(f"[INFO] Received {len(records)} records from Kinesis")
    # print(f"[DEBUG VARIABLES] RAW_EVENTS_BUCKET={RAW_EVENTS_BUCKET}, DYNAMO_TABLE_NAME={DYNAMO_TABLE_NAME}")

    for record in records:
        eeg_event: Dict[str, Any] = decode_kinesis_record(record)

        store_event_in_s3(eeg_event)
        update_dynamodb(eeg_event)

    return {
        "statusCode": 200,
        "processed_records": len(records),
    }
