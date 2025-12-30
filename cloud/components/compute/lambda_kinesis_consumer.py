from typing import Final

import pulumi
import pulumi_aws as aws


# ============================================================
# Constants
# ============================================================

LAMBDA_FUNCTION_NAME: Final[str] = "eeg-seizure-kinesis-consumer"
LAMBDA_HANDLER: Final[str] = "handler.handler"
LAMBDA_RUNTIME: Final[str] = "python3.11"


def create_kinesis_consumer_lambda(
    *,
    role_arn: pulumi.Input[str],
) -> aws.lambda_.Function:
    """
    Create the Lambda function that will consume EEG events
    from Kinesis (trigger added later).

    Parameters
    ----------
    role_arn : pulumi.Input[str]
        ARN of the IAM role for Lambda execution.

    Returns
    -------
    aws.lambda_.Function
        The created Lambda function.
    """

    lambda_function: aws.lambda_.Function = aws.lambda_.Function(
        resource_name="eegSeizureKinesisConsumerLambda",
        name=LAMBDA_FUNCTION_NAME,
        runtime=LAMBDA_RUNTIME,
        handler=LAMBDA_HANDLER,
        role=role_arn,
        code=pulumi.AssetArchive(
            {
                ".": pulumi.FileArchive(
                    "lambda_src/kinesis_consumer"
                )
            }
        ),
        timeout=30,
        memory_size=256,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Compute",
            "Purpose": "KinesisConsumer",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    return lambda_function
