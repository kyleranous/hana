from django.urls import path

from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nodes/<str:node_id>', views.node_detail, name='node_detail'),
]