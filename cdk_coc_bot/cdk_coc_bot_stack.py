import os

import aws_cdk.aws_ec2 as ec2
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ssm as ssm
from aws_cdk import core

DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE") or "gabrielmichelwizeline/coc-bot:latest"


class CdkCocBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "vpc")
        cluster = ecs.Cluster(self, "coc-bot-cluster", vpc=vpc)

        DEVELOPER_EMAIL_COC_API = ssm.StringParameter.from_string_parameter_attributes(
            self, "DEVELOPER_EMAIL_COC_API", parameter_name="DEVELOPER_EMAIL_COC_API"
        )
        DEVELOPER_PASSWORD_COC_API = (
            ssm.StringParameter.from_string_parameter_attributes(
                self,
                "DEVELOPER_PASSWORD_COC_API",
                parameter_name="DEVELOPER_PASSWORD_COC_API",
            )
        )
        DISCORD_BOT_TOKEN = ssm.StringParameter.from_string_parameter_attributes(
            self, "DISCORD_BOT_TOKEN", parameter_name="DISCORD_BOT_TOKEN"
        )

        auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            min_capacity=1,
            max_capacity=1,
        )

        capacity_provider = ecs.AsgCapacityProvider(
            self, "AsgCapacityProvider", auto_scaling_group=auto_scaling_group
        )
        cluster.add_asg_capacity_provider(capacity_provider)

        ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "coc-bot-discord-service",
            cluster=cluster,
            memory_limit_mib=128,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(DOCKER_IMAGE),
                secrets={
                    "DEVELOPER_EMAIL_COC_API": ecs.Secret.from_ssm_parameter(
                        DEVELOPER_EMAIL_COC_API
                    ),
                    "DEVELOPER_PASSWORD_COC_API": ecs.Secret.from_ssm_parameter(
                        DEVELOPER_PASSWORD_COC_API
                    ),
                    "DISCORD_BOT_TOKEN": ecs.Secret.from_ssm_parameter(
                        DISCORD_BOT_TOKEN
                    ),
                },
                family="coc-bot",
            ),
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=0
        )
