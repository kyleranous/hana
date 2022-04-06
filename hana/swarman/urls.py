from django.urls import (
    path,
    include,
)

from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<int:swarm_id>', views.swarm_dashboard, name='swarm-dashboard'),
    path('nodes/<str:node_id>', views.node_detail, name='node-detail'),
    path('new_swarm/', views.AddSwarm.as_view(), name='new-swarm'),
    path('create_swarm/', views.create_swarm, name='create-swarm'),
    path('api/', include('swarman.api.urls')),

]
