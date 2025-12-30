# cloud/components/analytics/glue_table.py
from __future__ import annotations

from typing import Final
import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

GLUE_TABLE_NAME: Final[str] = "eeg_window_events"

# ============================================================
# Glue Table
# ============================================================

def create_glue_table(
    *,
    database_name: pulumi.Input[str],
    data_lake_bucket_name: pulumi.Input[str],
) -> aws.glue.CatalogTable:
    """
    Creates a Glue Catalog Table over EEG window-level JSON events stored in S3.
    """

    table: aws.glue.CatalogTable = aws.glue.CatalogTable(
        resource_name="eegSeizureEventsTable",
        database_name=database_name,
        name=GLUE_TABLE_NAME,
        table_type="EXTERNAL_TABLE",
        parameters={
            "classification": "json",
        },
        storage_descriptor=aws.glue.CatalogTableStorageDescriptorArgs(
            location=data_lake_bucket_name.apply(
                lambda b: f"s3://{b}/events/"
            ),
            input_format="org.apache.hadoop.mapred.TextInputFormat",
            output_format="org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat",
            ser_de_info={
                "serializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                "parameters": {
                    "ignore.malformed.json": "true",
                },
            },
            columns=[
                {"name": "event_type", "type": "string"},
                {"name": "room_id", "type": "string"},
                {"name": "patient_id", "type": "string"},
                {"name": "session_id", "type": "string"},
                {"name": "window_index", "type": "int"},
                {"name": "score", "type": "double"},
                {"name": "suspected", "type": "boolean"},
                {"name": "timestamp", "type": "string"},
            ],
        ),
    )

    pulumi.export("glue_table_name", table.name)

    return table
