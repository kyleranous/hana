from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser

import json

from swarman.models import Swarm, Node
from .serializers import SwarmSerializer, NodeSerializer
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
                    swarm = Swarm.objects.filter(id=request.data['swarm_id']).first()
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

                    return Response({'success' : 'All Nodes Added Successfully'}, status=status.HTTP_201_CREATED)
        
            return Response({'error': "Field is Required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "swarm_id is Required"}, status=status.HTTP_400_BAD_REQUEST)