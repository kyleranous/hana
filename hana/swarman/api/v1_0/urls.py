from django.urls import path

from .api_views import (
    SwarmViewSet,
    NodeList,
    get_existing_swarm_nodes,
    add_existing_swarm_nodes,
    leave_swarm,
    update_node_availability,
    promote_node,
    demote_node,
    node_utilization,
    sync_node_data,
)


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
    path('swarms/<int:swarm_id>/nodes', NodeList.as_view(),
         name='api-node-list'),
    path('swarms/existing_swarm_nodes', get_existing_swarm_nodes,
         name="api-existing-swarm-nodes"),
    path('swarms/add_existing_swarm_nodes',
         add_existing_swarm_nodes, name="api-add-swarm-nodes"),

    path('nodes/<int:node_id>/leave', leave_swarm, name='api-leave-swarm'),
    path('nodes/<int:node_id>/promote', promote_node, name='api-node-promote'),
    path('nodes/<int:node_id>/demote', demote_node, name='api-node-demote'),
    path('nodes/<int:node_id>/utilization',
         node_utilization, name='api-node-utilization'),
    path('nodes/<int:node_id>/update', update_node_availability,
         name='api-update-node'),
    path('nodes/<int:node_id>/sync', sync_node_data, name='api-sync-node')
]
