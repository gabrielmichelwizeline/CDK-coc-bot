from aws_cdk import (
        core,
        assertions
    )

from cdk_coc_bot.cdk_coc_bot_stack import CdkCocBotStack


def test_sqs_queue_created():
    app = core.App()
    stack = CdkCocBotStack(app, "cdk-coc-bot")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = CdkCocBotStack(app, "cdk-coc-bot")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
