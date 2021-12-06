import os

import aws_cdk.aws_ec2 as ec2
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_ssm as ssm

DEVELOPER_EMAIL_COC_API = os.environ.get("DEVELOPER_EMAIL_COC_API") or ""
DEVELOPER_PASSWORD_COC_API = os.environ.get("DEVELOPER_PASSWORD_COC_API") or ""
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") or ""
DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE") or "gabrielmichelwizeline/coc-bot:latest"


class CdkCocBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, 'vpc')
        cluster = ecs.Cluster(self, "coc-bot-cluster")

        param = ssm.StringParameter.from_string_parameter_attributes(self, "MyParameter", parameter_name='DEVELOPER_EMAIL_COC_API')

        print((param))
        a = ecs.Secret.from_ssm_parameter(param)
        print(a)
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

        load_balanced_ecs_service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "coc-bot-discord-service",
            cluster=cluster,
            memory_limit_mib=128,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(DOCKER_IMAGE),
                environment={
                    "DEVELOPER_PASSWORD_COC_API": DEVELOPER_PASSWORD_COC_API,
                    "DISCORD_BOT_TOKEN": DISCORD_BOT_TOKEN,
                },
                secrets={
                     "DEVELOPER_EMAIL_COC_API": a,
                },
                family='coc-bot'
            ),
            desired_count=1,
            min_healthy_percent=0,
        )
