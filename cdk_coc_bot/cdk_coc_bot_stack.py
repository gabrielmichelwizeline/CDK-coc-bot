import os

import aws_cdk.aws_ec2 as ec2
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core

DEVELOPER_EMAIL_COC_API = os.environ.get("DEVELOPER_EMAIL_COC_API")
DEVELOPER_PASSWORD_COC_API = os.environ.get("DEVELOPER_PASSWORD_COC_API")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE")

class CdkCocBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC", max_azs=1)
        cluster = ecs.Cluster(self, "coc-bot-cluster", vpc=vpc)

        security_group = ec2.SecurityGroup(self, "coc-bot-sg", vpc=vpc)
        auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            min_capacity=1,
            max_capacity=1,
            security_group=security_group,
        )

        capacity_provider = ecs.AsgCapacityProvider(
            self, "AsgCapacityProvider", auto_scaling_group=auto_scaling_group
        )
        cluster.add_asg_capacity_provider(capacity_provider)

        load_balanced_ecs_service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "coc-bot-discord-service",
            cluster=cluster,
            memory_limit_mib=128,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(DOCKER_IMAGE),
                secrets={
                    "DEVELOPER_EMAIL_COC_API": DEVELOPER_EMAIL_COC_API,
                    "DEVELOPER_PASSWORD_COC_API": DEVELOPER_PASSWORD_COC_API,
                    "DISCORD_BOT_TOKEN": DISCORD_BOT_TOKEN,
                },
            ),
            desired_count=1,
        )
