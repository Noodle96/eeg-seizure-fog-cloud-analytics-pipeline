# cloud/components/analytics/athena.py
from __future__ import annotations

from typing import Final
import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

ATHENA_WORKGROUP_NAME: Final[str] = "eeg-seizure-athena-wg"

# ============================================================
# Athena WorkGroup
# ============================================================

def create_athena_workgroup(
    results_bucket_name: pulumi.Input[str],
) -> aws.athena.Workgroup:
    """
    Creates an Athena WorkGroup for querying EEG seizure events.
    """

    workgroup: aws.athena.Workgroup = aws.athena.Workgroup(
        resource_name="eegSeizureAthenaWorkgroup",
        name=ATHENA_WORKGROUP_NAME,
        state="ENABLED",
        configuration=aws.athena.WorkgroupConfigurationArgs(
            enforce_workgroup_configuration=True,
            result_configuration=aws.athena.WorkgroupConfigurationResultConfigurationArgs(
                output_location=results_bucket_name.apply(
                    lambda bucket: f"s3://{bucket}/athena-results/"
                )
            ),
        ),
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Analytics",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    return workgroup
