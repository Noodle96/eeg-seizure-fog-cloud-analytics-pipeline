import pulumi
import pulumi_aws as aws

# =========================
# Streaming layer
# =========================
from components.streaming.kinesis import create_eeg_event_stream

# =========================
# Storage layer
# =========================
from components.storage.s3 import create_s3_buckets

# =========================
# Database layer
# =========================
from components.database.dynamodb import create_session_state_table

# =========================
# Security layer
# =========================
from components.security.iam_lambda_role import create_kinesis_consumer_lambda_role

# =========================
# Compute layer
# =========================
from components.compute.lambda_kinesis_consumer import (
    create_kinesis_consumer_lambda,
)

# =========================
# Streaming layer
# =========================
from components.streaming.kinesis_event_mapping import (
    create_kinesis_lambda_event_mapping,
)

# ============================================================
# Glue + Athena (EEG Events Analytics)
# ============================================================
from components.analytics.glue_database import create_glue_database
from components.analytics.glue_table import create_glue_table
from components.analytics.athena import create_athena_workgroup


# ============================================================
# SNS + Dynamo Alerts
# ============================================================
from components.messaging.sns import create_eeg_seizure_alerts_topic
from components.compute.lambda_eeg_alert import (
    create_eeg_alert_lambda,
    create_dynamodb_stream_event_source_mapping,
    EEGAlertLambdaArgs,
)
from components.security.iam import create_lambda_execution_role

# ============================================================
# 1. Create Kinesis Data Stream for EEG events
# ============================================================
eeg_event_stream: aws.kinesis.Stream = create_eeg_event_stream()

# ============================================================
# 2. Create S3 buckets
# ============================================================
data_lake_bucket: aws.s3.Bucket
athena_results_bucket: aws.s3.Bucket
data_lake_bucket, athena_results_bucket = create_s3_buckets()

# ============================================================
# 3. Create DynamoDB table (session state)
# ============================================================
session_state_table: aws.dynamodb.Table = create_session_state_table()

# ============================================================
# 4. Create IAM Role for Kinesis Consumer Lambda
# ============================================================
lambda_execution_role: aws.iam.Role = create_kinesis_consumer_lambda_role(
    data_lake_bucket=data_lake_bucket,
    session_state_table=session_state_table,
    kinesis_stream=eeg_event_stream,
)

# ============================================================
# 4. Create Lambda
# ============================================================

kinesis_consumer_lambda: aws.lambda_.Function = create_kinesis_consumer_lambda(
    role_arn=lambda_execution_role.arn,
)

# ============================================================
# 5. Connect Lambda ← Kinesis
# ============================================================
kinesis_lambda_mapping = create_kinesis_lambda_event_mapping(
    kinesis_stream_arn=eeg_event_stream.arn,
    lambda_function_arn=kinesis_consumer_lambda.arn,
)

# ============================================================
# Glue + Athena (EEG Events Analytics)
# ============================================================
# 1. Glue Database
glue_database: aws.glue.CatalogDatabase = create_glue_database()

# 2. Glue Table (JSON events)
glue_table: aws.glue.CatalogTable = create_glue_table(
    database_name=glue_database.name,
    data_lake_bucket_name=data_lake_bucket.bucket,
)

# 3. Athena WorkGroup
athena_workgroup: aws.athena.Workgroup = create_athena_workgroup(
    results_bucket_name=athena_results_bucket.bucket,
)

# ============================================================
# SNS + Dynamo Alerts
# ============================================================

# SNS
alerts_topic = create_eeg_seizure_alerts_topic(
    email_subscription="jorgealfredo.jatc@gmail.com"
)
alerts_lambda_role = create_lambda_execution_role()
alerts_lambda = create_eeg_alert_lambda(
    EEGAlertLambdaArgs(
        role_arn=alerts_lambda_role.arn,
        table_name=session_state_table.name,
        dynamodb_stream_arn=session_state_table.stream_arn,
        sns_topic_arn=alerts_topic.arn,
    )
)

create_dynamodb_stream_event_source_mapping(
    dynamodb_stream_arn=session_state_table.stream_arn,
    lambda_function_arn=alerts_lambda.arn,
)


# ============================================================
# Stack outputs
# ============================================================
pulumi.export("eeg_kinesis_stream_name", eeg_event_stream.name)
pulumi.export("eeg_kinesis_stream_arn", eeg_event_stream.arn)

pulumi.export("data_lake_bucket_name", data_lake_bucket.bucket)
pulumi.export("athena_results_bucket_name", athena_results_bucket.bucket)

pulumi.export("dynamodb_table_name", session_state_table.name)
pulumi.export("dynamodb_table_arn", session_state_table.arn)
pulumi.export("dynamodb_stream_arn", session_state_table.stream_arn)

pulumi.export("lambda_execution_role_arn", lambda_execution_role.arn)

pulumi.export("kinesis_consumer_lambda_name", kinesis_consumer_lambda.name)
pulumi.export("kinesis_consumer_lambda_arn", kinesis_consumer_lambda.arn)

pulumi.export("kinesis_lambda_event_mapping_id", kinesis_lambda_mapping.id)
