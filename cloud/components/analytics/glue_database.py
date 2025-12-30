# cloud/components/analytics/glue_database.py
from __future__ import annotations

from typing import Final
import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

GLUE_DATABASE_NAME: Final[str] = "eeg_seizure_events_db"

# ============================================================
# Glue Database
# ============================================================

def create_glue_database() -> aws.glue.CatalogDatabase:
    """
    Creates a Glue Data Catalog database for EEG seizure events.
    """

    glue_database: aws.glue.CatalogDatabase = aws.glue.CatalogDatabase(
        resource_name="eegSeizureGlueDatabase",
        name=GLUE_DATABASE_NAME,
        description="Glue database for EEG window-level seizure events stored in S3",
    )

    pulumi.export("glue_database_name", glue_database.name)

    return glue_database
