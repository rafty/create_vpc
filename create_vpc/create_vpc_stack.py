import aws_cdk
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2
from aws_cdk import Tags


class CreateVpcStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            vpc_name: str,
            vpc_cidr: str,
            env: aws_cdk.Environment,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = aws_ec2.Vpc(
            self,
            'Vpc',
            vpc_name=vpc_name,
            cidr=vpc_cidr,
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                #
                # EKS cluster for app
                #
                aws_ec2.SubnetConfiguration(
                    name="Front-app",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    cidr_mask=24),
                aws_ec2.SubnetConfiguration(
                    name="Application-app",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24),
                aws_ec2.SubnetConfiguration(
                    name="DataStore-app",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24),
                #
                # EKS cluster for argocd
                #
                aws_ec2.SubnetConfiguration(
                    name="Front-argocd",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    cidr_mask=24),
                aws_ec2.SubnetConfiguration(
                    name="Application-argocd",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24),
            ]
        )

        self.tag_subnet_for_eks_cluster(vpc)

    def tag_subnet_for_eks_cluster(self, vpc):
        # VPCに複数のEKS Clusterがある場合、Tag:"kubernetes.io/cluster/cluster-name": "shared"が必要
        # PrivateSubnetにはTag "kubernetes.io/role/internal-elb": '1'
        # PublicSubnetには"kubernetes.io/role/elb": '1'
        # https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/network_reqs.html
        # https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/alb-ingress.html

        print('-----------subnet tagging-----------------------')

        eks_cluster_name = ['gitops_eks', 'app_eks']

        self.tag_all_subnets(vpc.public_subnets, 'kubernetes.io/role/elb', '1')
        self.tag_all_subnets(vpc.private_subnets, 'kubernetes.io/role/internal-elb', '1')

        for cluster_name in eks_cluster_name:
            self.tag_all_subnets(vpc.public_subnets,
                                 f'kubernetes.io/cluster/{cluster_name}', 'shared')
            self.tag_all_subnets(vpc.private_subnets,
                                 f'kubernetes.io/cluster/{cluster_name}', 'shared')

    @staticmethod
    def tag_all_subnets(subnets, tag_name, tag_value):
        for subnet in subnets:
            Tags.of(subnet).add(tag_name, tag_value)

        # aws_cdk.CfnOutput(
        #     self,
        #     'VpcStackOutput',
        #     value=vpc.vpc_id,
        #     export_name=f'vpc_id__{vpc_name}')
