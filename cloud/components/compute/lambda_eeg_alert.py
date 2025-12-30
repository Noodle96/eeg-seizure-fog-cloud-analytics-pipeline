# components/compute/lambda_eeg_alert.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pulumi
import pulumi_aws as aws

LAMBDA_NAME: Final[str] = "EEGSeizureAlertLambda"
LAMBDA_HANDLER: Final[str] = "handler.handler"
LAMBDA_RUNTIME: Final[str] = "python3.13"


@dataclass(frozen=True)
class EEGAlertLambdaArgs:
    role_arn: pulumi.Input[str]
    table_name: pulumi.Input[str]
    dynamodb_stream_arn: pulumi.Input[str]
    sns_topic_arn: pulumi.Input[str]


def create_eeg_alert_lambda(args: EEGAlertLambdaArgs) -> aws.lambda_.Function:
    """
    Lambda that consumes DynamoDB Streams and sends alerts to SNS.
    """

    lambda_code: pulumi.AssetArchive = pulumi.AssetArchive(
        {
            ".": pulumi.FileArchive("../cloud/lambda_src/dynamo_alerts/"),
        }
    )

    fn: aws.lambda_.Function = aws.lambda_.Function(
        resource_name="eegSeizureAlertLambda",
        name=LAMBDA_NAME,   
        role=args.role_arn,
        runtime=LAMBDA_RUNTIME,
        handler=LAMBDA_HANDLER,
        timeout=30,
        memory_size=256,
        code=lambda_code,
        environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "TABLE_NAME": args.table_name,
                "SNS_TOPIC_ARN": args.sns_topic_arn,
                "SUSPECTED_THRESHOLD": "1",
            }
        ),
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    return fn


def create_dynamodb_stream_event_source_mapping(
    *,
    dynamodb_stream_arn: pulumi.Input[str],
    lambda_function_arn: pulumi.Input[str],
) -> aws.lambda_.EventSourceMapping:
    """
    DynamoDB Stream → Lambda mapping.
    """

    return aws.lambda_.EventSourceMapping(
        resource_name="dynamoStreamToEEGAlertsLambda",
        event_source_arn=dynamodb_stream_arn,
        function_name=lambda_function_arn,
        starting_position="LATEST",
        batch_size=2,
        enabled=True,
    )
