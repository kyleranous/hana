from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

import json
import docker

from swarman.models import (
    Swarm,
    Node,
    Service,
)
from .serializers import (
    SwarmSerializer,
    NodeSerializer,
    NodeUpdateSerializer,
)
from . import api_utils


class SwarmViewSet(viewsets.ModelViewSet):
    """
    List all Swarms, create a new Swarm Entry, or view Swarm Details
    """
    queryset = Swarm.objects.all()
    serializer_class = SwarmSerializer

    def perform_create(self, serializer):
        serializer.save()


class NodeList(APIView):
    """
    List all Nodes belonging to a swarm
    """

    def get(self, request, swarm_id, format=None):

        swarm = Swarm.objects.filter(id=swarm_id).first()
        nodes = swarm.nodes.all()

        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def get_existing_swarm_nodes(request):
    """ 
    Takes in an IP address or Hostname and port for an existing swarm
    and retrieves a list of nodes belonging to the swarm. Used when adding
    an existing Swarm to the HANA Swarm Manager through the HANA UI.
    Docker API v1.41
    """
    if request.method == 'POST':
        # Verify request is in expected format
        if "swarm_address" in request.data.keys():
            if request.data['swarm_address'] != "":
                # Sanitize url to remove any attachments
                url = request.data['swarm_address'].split('//')[-1]
                url = url.split('/')[0]

                # Attempt fetch node info from swarm_address

                node_data = api_utils.get_existing_node_info(url)
                if 'error' in node_data.keys():
                    return Response(json.dumps(node_data), status=status.HTTP_400_BAD_REQUEST)

                return Response(json.dumps(node_data), status=status.HTTP_200_OK)

        return Response({'error': "Field is Required"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_existing_swarm_nodes(request):
    """
    Takes in an IP address or Hostname and port for an existing swarm,
    retrieves a list of nodes belonging to the swarm, and adds them to the 
    database. Used when adding an existing Swarm to the HANA Swarm Manager 
    through the HANA UI.
    Docker API v1.41
    """
    if request.method == 'POST':
        if "swarm_id" in request.data.keys():
            if "swarm_address" in request.data.keys():
                if request.data['swarm_address'] != "":
                    # Sanitize url to remove any attachments
                    url = request.data['swarm_address'].split('//')[-1]
                    url = url.split('/')[0]

                    # Attempt fetch node info from swarm_address

                    node_data = api_utils.get_existing_node_info(url)
                    if 'error' in node_data.keys():
                        return Response(json.dumps(node_data), status=status.HTTP_400_BAD_REQUEST)

                    # Add Nodes to Swarm
                    swarm = Swarm.objects.filter(
                        id=request.data['swarm_id']).first()
                    tokens = api_utils.get_swarm_tokens(url)
                    swarm.manager_join_token = tokens['Manager']
                    swarm.worker_join_token = tokens['Worker']
                    swarm.save()

                    for node in node_data['nodes']:
                        Node.objects.create(hostname=node['hostname'],
                                            ip_address=node['ip_address'],
                                            api_port=2375,
                                            role=node['role'],
                                            swarm=swarm,
                                            docker_version_index=node['docker_version_index'],
                                            node_architecture=node['node_architecture'],
                                            node_id=node['node_id'])

                    return Response({'success': 'All Nodes Added Successfully'}, status=status.HTTP_201_CREATED)

            return Response({'error': "Field is Required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "swarm_id is Required"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def leave_swarm(request, node_id):
    """
    Node Leaves a Swarm. Node remains in the database
    and can be re-added to another swarm. Swarm will still
    list the node, however will not assisgn tasks.
    """
    node = get_object_or_404(Node, pk=node_id)

    if node.leave_swarm():
        return Response(json.dumps({'success': 'Node left swarm'}), status=status.HTTP_200_OK)

    return Response({'error': 'Node did not leave swarm'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def promote_node(request, node_id):
    """
    Promotes a node to manager if able
    """
    node = get_object_or_404(Node, id=node_id)

    if node.promote():
        return Response(json.dumps({'success': 'Node Promoted Successfully'}), status=status.HTTP_200_OK)

    return Response({'error': 'Node was not promoted'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def demote_node(request, node_id):
    """
    Demotes a node to worker if able
    """
    node = get_object_or_404(Node, id=node_id)

    if node.demote():
        return Response(json.dumps({'success': 'Node Demoted Successfully'}),
                        status=status.HTTP_200_OK)

    return Response({'error': 'Node was not Demoted'},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def node_utilization(request, node_id):
    """
    Polls a Node and gets the resource utilization of each container running 
    on the node. Returns a Dictionary with Container Name, CPU Utilization, and 
    Memory Utilization
    """

    node = get_object_or_404(Node, id=node_id)

    return Response(node.utilization_per_container(), status=status.HTTP_200_OK)


@api_view(['POST'])
def update_node_availability(request, node_id):
    """
    Updates node availability state. Available states 'active', 'drain', 'pause'
    Ex:
    {
        "Availability" : "active",
        "Role" : 'worker'
    }
    """
    node = get_object_or_404(Node, id=node_id)

    if request.method == 'POST':
        if "Availability" in request.data.keys():

            if request.data['Availability'] in ('active', 'pause', 'drain'):

                try:
                    for address in node.swarm.manager_ip_list():
                        client = docker.DockerClient(
                            base_url=f"tcp://{address}")
                        update_package = {
                            'Availability': request.data['Availability'],
                            'Role': node.role
                        }
                        print(address)
                        print(update_package)
                        update_node = client.nodes.get(node.hostname)
                        print(update_node.attrs)
                        update_node.reload()
                        if update_node.update(update_package):
                            return Response({"Success": "Node Updated Successfully"},
                                            status=status.HTTP_200_OK)

                except:
                    return Response({"Error": "Error Updating Node"},
                                    status=status.HTTP_504_GATEWAY_TIMEOUT)

            else:
                return Response({"Error": "Invalid Availability State"},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"Error": "Availability is a required key"},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def sync_node_data(request, node_id):
    """
    Syncs the Node entry in the database to the information pulled from the
    docker API
    """
    node = get_object_or_404(Node, id=node_id)
    try:
        for address in node.swarm.manager_ip_list():
            client = docker.DockerClient(
                base_url=f"tcp://{address}")
            node_data = client.nodes.get(node.hostname).attrs

            # role
            node.role = node_data['Spec']['Role'].title()
            # node_architecture
            node.node_architecture = node_data['Description']['Platform']['Architecture']
            # node_id
            node.node_id = node_data['ID']
            # total_memory
            node.total_memory = node_data['Description']['Resources']['MemoryBytes']/(
                10**9)
            # cpu_count
            node.cpu_count = node_data['Description']['Resources']['NanoCPUs']/(
                10**9)
            # os
            node.os = node_data['Description']['Platform']['OS']
            # docker_engine
            node.docker_engine = node_data['Description']['Engine']['EngineVersion']

            node.save()

            return Response({'Success': 'Node entry synced'},
                            status=status.HTTP_200_OK)

    except:
        return Response({"Error": "Error connecting to node"},
                        status=status.HTTP_504_GATEWAY_TIMEOUT)


@api_view(['POST'])
def service_scale(request):
    """
    Scale a service to a desired number of replicas.
    ex:
    {
        "swarm_id": 3,
        "service_id": "9mnpnzenvg8p8tdbtq4wvbkcz", 
        "replicas": 4
    }
    """
    if request.method == "POST":

        swarm = get_object_or_404(Swarm, id=request.data['swarm_id'])

        for address in swarm.manager_ip_list():
            try:
                client = docker.DockerClient(base_url=f'tcp://{address}')
                service = client.services.get(request.data['service_id'])
                
                if service.scale(int(request.data['replicas'])):
                    client.close()
                    return Response({"Success": f"Scaled service to {request.data['replicas']}"},
                                    status=status.HTTP_200_OK)
            except:
                client.close()

        return Response({'Error': 'Error Connecting to Swarm'},
                        status=status.HTTP_504_GATEWAY_TIMEOUT)
