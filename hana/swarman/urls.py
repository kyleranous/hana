from django.urls import path

from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nodes/<str:node_id>', views.node_detail, name='node_detail'),
    path('new_swarm/', views.new_swarm, name='new_swarm'),
    path('create_swarm/', views.create_swarm, name='create_swarm')
]