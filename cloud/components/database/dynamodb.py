from typing import Final

import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

TABLE_NAME: Final[str] = "eeg-seizure-session-state"
PARTITION_KEY: Final[str] = "pk"
SORT_KEY: Final[str] = "sk"


def create_session_state_table() -> aws.dynamodb.Table:
    """
    Create a DynamoDB table to store live session and patient state.

    This table stores aggregated counters and metadata derived from
    EEG window events (normal and suspected).

    Returns
    -------
    aws.dynamodb.Table
        The created DynamoDB table.
    """

    table: aws.dynamodb.Table = aws.dynamodb.Table(
        resource_name="eegSeizureSessionStateTable",
        name=TABLE_NAME,
        billing_mode="PAY_PER_REQUEST",
        hash_key=PARTITION_KEY,
        range_key=SORT_KEY,
        attributes=[
            aws.dynamodb.TableAttributeArgs(
                name=PARTITION_KEY,
                type="S",
            ),
            aws.dynamodb.TableAttributeArgs(
                name=SORT_KEY,
                type="S",
            ),
        ],
        stream_enabled=True,
        stream_view_type="NEW_AND_OLD_IMAGES",
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Database",
            "Purpose": "SessionState",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    return table
