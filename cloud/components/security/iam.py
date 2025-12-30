# components/security/iam.py
from __future__ import annotations

from typing import Final, List

import pulumi
import pulumi_aws as aws

LAMBDA_ROLE_NAME: Final[str] = "Lambda_EEG_Alerts_Role"

MANAGED_POLICY_ARNS: Final[List[str]] = [
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",  # 🔑 Streams incluidos
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
]


def create_lambda_execution_role() -> aws.iam.Role:
    """
    IAM Role for EEG alert Lambda consuming DynamoDB Streams and publishing to SNS.
    """

    role: aws.iam.Role = aws.iam.Role(
        resource_name="eegAlertsLambdaRole",
        name=LAMBDA_ROLE_NAME,
        assume_role_policy=aws.iam.get_policy_document(
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
        ).json,
        tags={
            "Project": "EEGSeizureFogCloudAnalyticsPipeline",
            "ManagedBy": "Pulumi",
            "Environment": pulumi.get_stack(),
        },
    )

    for idx, policy_arn in enumerate(MANAGED_POLICY_ARNS):
        aws.iam.RolePolicyAttachment(
            resource_name=f"eegAlertsLambdaPolicy-{idx}",
            role=role.name,
            policy_arn=policy_arn,
        )

    return role
