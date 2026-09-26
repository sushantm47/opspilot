#!/usr/bin/env python3
"""AWS CDK app. Deploy:  cd infra && pip install -r requirements.txt && cdk deploy -c stage=beta"""

import aws_cdk as cdk

from stack import OpsPilotStack

app = cdk.App()
stage = app.node.try_get_context("stage") or "beta"
OpsPilotStack(app, f"OpsPilot-{stage}", stage=stage)
app.synth()
