from typing import Final

import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

STREAM_NAME: Final[str] = "eeg-seizure-event-stream"
RETENTION_HOURS: Final[int] = 24
SHARD_COUNT: Final[int] = 1


def create_eeg_event_stream() -> aws.kinesis.Stream:
    """
    Create the Kinesis Data Stream used to ingest EEG window events
    from the Fog layer.

    This stream carries both normal and suspected EEG window events.

    Returns
    -------
    aws.kinesis.Stream
        The created Kinesis Data Stream.
    """

    stream: aws.kinesis.Stream = aws.kinesis.Stream(
        resource_name="eegSeizureEventStream",
        name=STREAM_NAME,
        shard_count=SHARD_COUNT,
        retention_period=RETENTION_HOURS,
        stream_mode_details=aws.kinesis.StreamStreamModeDetailsArgs(
            stream_mode="PROVISIONED"
        ),
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
            "Layer": "Streaming",
        },
    )

    return stream
