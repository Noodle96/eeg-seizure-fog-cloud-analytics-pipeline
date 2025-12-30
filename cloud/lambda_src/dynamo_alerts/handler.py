import json
import os
import boto3

sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
THRESHOLD = int(os.environ["SUSPECTED_THRESHOLD"])

def handler(event, context):
    print("[handler] def handler")
    print(f"[handler] sns_topic_arn: {SNS_TOPIC_ARN} - THRESHOLD: {THRESHOLD}")
    for record in event["Records"]:
        print(f"[DEBUG] Processing record: {json.dumps(record)}")
        if record["eventName"] not in ("INSERT", "MODIFY"):
            continue

        new_image = record["dynamodb"].get("NewImage")
        if not new_image:
            continue

        suspected = int(new_image["suspected_windows"]["N"])
        total = int(new_image["windows_total"]["N"])

        if suspected >= THRESHOLD:
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

    return {"statusCode": 200}
