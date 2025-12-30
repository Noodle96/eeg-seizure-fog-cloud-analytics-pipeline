from typing import Final

import pulumi_aws as aws


# ============================================================
# Constants
# ============================================================

BATCH_SIZE: Final[int] = 5
STARTING_POSITION: Final[str] = "LATEST"


def create_kinesis_lambda_event_mapping(
    *,
    kinesis_stream_arn: str,
    lambda_function_arn: str,
) -> aws.lambda_.EventSourceMapping:
    """
    Connect a Kinesis Data Stream to a Lambda function.

    Parameters
    ----------
    kinesis_stream_arn : str
        ARN of the Kinesis stream.
    lambda_function_arn : str
        ARN of the Lambda function.

    Returns
    -------
    aws.lambda_.EventSourceMapping
        The created event source mapping.
    """

    mapping: aws.lambda_.EventSourceMapping = aws.lambda_.EventSourceMapping(
        resource_name="eegSeizureKinesisEventMapping",
        event_source_arn=kinesis_stream_arn,
        function_name=lambda_function_arn,
        starting_position=STARTING_POSITION,
        batch_size=BATCH_SIZE,
        enabled=True,
    )

    return mapping
