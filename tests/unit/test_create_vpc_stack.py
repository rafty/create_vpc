import aws_cdk as core
import aws_cdk.assertions as assertions

from create_vpc.create_vpc_stack import CreateVpcStack

# example tests. To run these tests, uncomment this file along with the example
# resource in create_vpc/create_vpc_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CreateVpcStack(app, "create-vpc")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
