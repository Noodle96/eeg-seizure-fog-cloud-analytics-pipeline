# components/messaging/sns.py
from __future__ import annotations

from typing import Final, Optional

import pulumi
import pulumi_aws as aws

TOPIC_NAME: Final[str] = "EEG_Seizure_Alerts"


def create_eeg_seizure_alerts_topic(
    topic_name: str = TOPIC_NAME,
    email_subscription: Optional[str] = None,
) -> aws.sns.Topic:
    """
    Create SNS Topic for EEG seizure alerts.
    """

    topic: aws.sns.Topic = aws.sns.Topic(
        resource_name="eegSeizureAlertsTopic",
        name=topic_name,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    if email_subscription is not None:
        aws.sns.TopicSubscription(
            resource_name="eegSeizureAlertsEmailSubscription",
            topic=topic.arn,
            protocol="email",
            endpoint=email_subscription,
        )

    return topic
