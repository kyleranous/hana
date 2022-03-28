from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse


from swarman.models import Swarm, Node
from .serializers import SwarmSerializer, NodeSerializer


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
        