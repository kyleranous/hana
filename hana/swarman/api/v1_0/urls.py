from django.urls import path, include

from .api_views import SwarmViewSet, NodeList, get_existing_swarm_nodes, add_existing_swarm_nodes


swarm_list = SwarmViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

swarm_detail = SwarmViewSet.as_view({
    'get': 'retrieve',
})


urlpatterns = [
    path('swarms/', swarm_list, name='api-swarm-list'),
    path('swarms/<int:pk>', swarm_detail, name='api-swarm-detail'),
    path('swarms/<int:swarm_id>/nodes', NodeList.as_view(), name='api-node-list'),
    path('swarms/existing_swarm_nodes', get_existing_swarm_nodes, name="existing-swarm-nodes"),
    path('swarms/add_existing_swarm_nodes', add_existing_swarm_nodes, name="api-add-swarm-nodes")
]