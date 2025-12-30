from typing import Final

import pulumi
import pulumi_aws as aws


# ============================================================
# Constants
# ============================================================

ROLE_NAME: Final[str] = "eeg-seizure-kinesis-consumer-role"


def create_kinesis_consumer_lambda_role(
    *,
    data_lake_bucket: aws.s3.Bucket,
    session_state_table: aws.dynamodb.Table,
    kinesis_stream: aws.kinesis.Stream,
) -> aws.iam.Role:
    """
    Create IAM Role for the Lambda that consumes EEG events from Kinesis
    and writes to S3 and DynamoDB.

    Parameters
    ----------
    data_lake_bucket : aws.s3.Bucket
        S3 bucket for EEG data lake (events + EDF).
    session_state_table : aws.dynamodb.Table
        DynamoDB table for live session/patient state.
    kinesis_stream : aws.kinesis.Stream
        Kinesis Data Stream carrying EEG window events.

    Returns
    -------
    aws.iam.Role
        IAM role for the Lambda consumer.
    """

    # --------------------------------------------------------
    # Trust policy: allow Lambda to assume this role
    # --------------------------------------------------------
    assume_role_policy = aws.iam.get_policy_document(
        statements=[
            aws.iam.GetPolicyDocumentStatementArgs(
                effect="Allow",
                principals=[
                    aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                        type="Service",
                        identifiers=["lambda.amazonaws.com"],
                    )
                ],
                actions=["sts:AssumeRole"],
            )
        ]
    )

    role = aws.iam.Role(
        resource_name="eegSeizureLambdaRole",
        name=ROLE_NAME,
        assume_role_policy=assume_role_policy.json,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "Layer": "Security",
            "Purpose": "LambdaExecutionRole",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    # --------------------------------------------------------
    # Inline policy: minimal permissions
    # --------------------------------------------------------
    policy = aws.iam.Policy(
        resource_name="eegSeizureLambdaPolicy",
        policy=aws.iam.get_policy_document(
            statements=[
                # CloudWatch Logs
                aws.iam.GetPolicyDocumentStatementArgs(
                    effect="Allow",
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    resources=["arn:aws:logs:*:*:*"],
                ),
                # Kinesis read
                aws.iam.GetPolicyDocumentStatementArgs(
                    effect="Allow",
                    actions=[
                        "kinesis:GetRecords",
                        "kinesis:GetShardIterator",
                        "kinesis:DescribeStream",
                        "kinesis:ListStreams",
                    ],
                    resources=[kinesis_stream.arn],
                ),
                # S3 write (data lake)
                aws.iam.GetPolicyDocumentStatementArgs(
                    effect="Allow",
                    actions=["s3:PutObject"],
                    resources=[data_lake_bucket.arn.apply(lambda arn: f"{arn}/*")],
                ),
                # DynamoDB write/update (session state)
                aws.iam.GetPolicyDocumentStatementArgs(
                    effect="Allow",
                    actions=[
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                    ],
                    resources=[session_state_table.arn],
                ),
            ]
        ).json,
    )

    aws.iam.RolePolicyAttachment(
        resource_name="eegSeizureLambdaPolicyAttachment",
        role=role.name,
        policy_arn=policy.arn,
    )

    return role
