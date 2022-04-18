import graphene
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from swarman.models import Swarm, Node


class SwarmType(DjangoObjectType):

    node_count = graphene.Int()
    manager_count = graphene.Int()
    worker_count = graphene.Int()
    services_count = graphene.Int()
    service_list = graphene.List(GenericScalar)

    class Meta:
        model = Swarm
        description = "Swarm Specific Information"
        fields = (
            "id", 
            "swarm_name", 
            "manager_join_token", 
            "worker_join_token",
            "nodes"     
        )


class NodeType(DjangoObjectType):

    get_status = graphene.String()
    get_availability = graphene.String()
    get_utilization = GenericScalar(
        description = "Reports CPU and Memory utilization as percentage of available resources"
    )

    class Meta:
        model = Node
        description = "Node specific Information"
        fields = (
            "id",
            "hostname",
            "ip_address",
            "api_port",
            "role",
            "swarm",
            "node_architecture",
            "node_id",
            "total_memory",
            "cpu_count",
            "os",
            "docker_engine"
        )



class Query(graphene.ObjectType):
    
    swarm_by_name = graphene.Field(SwarmType, name=graphene.String(required=True),
        description="Get Swarm Information by Swarm Name")
    node_by_id = graphene.Field(NodeType, id=graphene.Int(required=True),
        description="Get Node Information by Database ID")

    class Meta:
        description = "Retrieve Information about Swarms and Nodes"

    def resolve_swarm_by_name(root, info, name):
        try:
            return Swarm.objects.get(swarm_name=name)
        except Swarm.DoesNotExist:
            return None

    def resolve_node_by_id(root, info, id):
        try:
            return Node.objects.get(id=id)
        except Node.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)