from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser

from swarman.models import Swarm, Node
from .serializers import SwarmSerializer, NodeSerializer
from . import api_utils


# API Views defined here
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'swarms': reverse('swarman:api-swarm-list', request=request, format=format),
    })


class SwarmViewSet(viewsets.ModelViewSet):
    """
    List all Swarms, or create a new Swarm Entry
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
    an existing Swarm to the HANA Swarm Manager.
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
                return Response({"swarm_address":url}, status=status.HTTP_200_OK)
        
        return Response({'error': "Field is Required"}, status=status.HTTP_400_BAD_REQUEST)

            