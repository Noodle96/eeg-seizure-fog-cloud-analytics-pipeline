from typing import Final, Tuple

import pulumi
import pulumi_aws as aws

# ============================================================
# Constants
# ============================================================

DATA_LAKE_BUCKET_NAME: Final[str] = "eeg-seizure-data-lake"
ATHENA_RESULTS_BUCKET_NAME: Final[str] = "eeg-seizure-athena-results"


def create_s3_buckets() -> Tuple[aws.s3.Bucket, aws.s3.Bucket]:
    """
    Create S3 buckets for:
    1) EEG data lake (events + EDF files)
    2) Athena query results

    Returns
    -------
    Tuple[aws.s3.Bucket, aws.s3.Bucket]
        (data_lake_bucket, athena_results_bucket)
    """

    # --------------------------------------------------------
    # EEG Data Lake Bucket
    # --------------------------------------------------------
    data_lake_bucket: aws.s3.Bucket = aws.s3.Bucket(
        resource_name="eegDataLakeBucket",
        bucket=DATA_LAKE_BUCKET_NAME,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Storage",
            "Purpose": "EEGDataLake",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    # --------------------------------------------------------
    # Athena Results Bucket
    # --------------------------------------------------------
    athena_results_bucket: aws.s3.Bucket = aws.s3.Bucket(
        resource_name="eegAthenaResultsBucket",
        bucket=ATHENA_RESULTS_BUCKET_NAME,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Analytics",
            "Purpose": "AthenaResults",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    return data_lake_bucket, athena_results_bucket
