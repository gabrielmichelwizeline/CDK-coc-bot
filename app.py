#!/usr/bin/env python3

from aws_cdk import core

from cdk_coc_bot.cdk_coc_bot_stack import CdkCocBotStack


app = core.App()
CdkCocBotStack(app, "cdk-coc-bot")

app.synth()
