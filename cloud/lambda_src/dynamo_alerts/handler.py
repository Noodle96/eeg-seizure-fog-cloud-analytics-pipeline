import json
import os
import boto3
from typing import Any, Dict, List

sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
THRESHOLD = int(os.environ["SUSPECTED_THRESHOLD"])

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = event.get("Records", [])
    print(f"[handler] Received {len(records)} records from DynamoDB Stream")
    print(f"[handler] event: {json.dumps(event)}")
    # print(f"[handler] sns_topic_arn: {SNS_TOPIC_ARN} - THRESHOLD: {THRESHOLD}")
    idx: int = 0
    for record in  records:
        print("record index:", idx)
        idx+=1
        print(f"[handler] Processing record: {json.dumps(record)}")
        if record["eventName"] not in ("INSERT", "MODIFY"):
            continue

        new_image = record["dynamodb"].get("NewImage")
        print(f"[handler] NewImage: {json.dumps(new_image)}")
        if not new_image:
            continue

        suspected = int(new_image["suspected_windows"]["N"])
        total = int(new_image["windows_total"]["N"])

        if suspected >= THRESHOLD:
            print("[handler] suspected >= THRESHOLD, sending alert")
            message = {
                "alert_type": "SESSION_THRESHOLD_EXCEEDED",
                "patient_id": new_image["pk"]["S"],
                "session_id": new_image["sk"]["S"],
                "suspected_windows": suspected,
                "windows_total": total,
            }

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠️ Alerta EEG: sesión sospechosa",
                Message=json.dumps(message, indent=2),
            )
        else:
            print("[handler] suspected < THRESHOLD, no alert sent")

    return {"statusCode": 200}
