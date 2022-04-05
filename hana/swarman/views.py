from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View

import requests
import json
import docker

from .models import Swarm, Node


SWARM_MANAGER_URL = 'http://192.168.1.200:2375'

# Create your views here.
def swarm_dashboard(request, swarm_id):
    """
    Display information about a swarm. Includes node and service status
    """
    swarm = get_object_or_404(Swarm, id=swarm_id)
    nodes = swarm.nodes.order_by('hostname')

    services = []

    for service in swarm.get_services():
        service_info = {
            'name' : service['Spec']['Name'],
            'ID' : service['ID'],
            'image' : service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0],
            'replicas' : service['Spec']['Mode']['Replicated']['Replicas'],
            'desired_tasks' : service['ServiceStatus']['DesiredTasks'],
            'target_port' : service['Endpoint']['Ports'][0]['TargetPort'],
            'published_port' : service['Endpoint']['Ports'][0]['PublishedPort'],
        }
        services.append(service_info)

    context = {
        "swarm" : swarm,
        "nodes" : nodes,
        "services" : services,
    }

    return render(request, 'swarman/swarm_dashboard.html', context)


def dashboard(request):
    """
    Displays information on nodes and services running on the swarm
    """

    node_response = requests.get(SWARM_MANAGER_URL + '/nodes')
    node_data = node_response.text

    nodes_json = json.loads(node_data)

    nodes = []
    for node in nodes_json:

        nodes.append((node['Description']['Hostname'], 
                      node['Status']['State'], 
                      node['Spec']['Role']))
        

    service_response = requests.get(SWARM_MANAGER_URL + '/services?status=1')
    print(SWARM_MANAGER_URL + '/services?status=1')
    service_data = service_response.text
    service_json = json.loads(service_data)
    services = []
    for service in service_json:
        services.append((service['Spec']['Name'],
                         service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0],
                         service['CreatedAt'],
                         service['Endpoint']['Ports'][0]['TargetPort'],
                         service['Endpoint']['Ports'][0]['PublishedPort']))
        
    context = {
    
        'nodes' : nodes,
        'services': services,
    }

    return render(request, 'swarman/dashboard.html', context)


def node_detail(request, node_id):
    """
    Displays Node Specific Details
    """
    # Get Node Object
    node = get_object_or_404(Node, id=node_id)

    # Get Container List
    try:
        #client = docker.DockerClient(base_url=f'tcp://{node.ip_address}:{node.api_port}')
        #containers = client.containers.list()
        containers = [{"Names":["/boring_feynman"], "Image": "ubuntu:latest", "Mounts": [{"Name": "test", "Source": "/data", "Destination" : "/data"}]},
                      {"Names":["/boring_feynman"], "Image": "ubuntu:latest", "Mounts": [{"Name": "test", "Source": "/data", "Destination" : "/data"}]}]
    except:
        containers = [{"error" : "Error retrieving containers"}]

    
    context = {
        'node' : node,
        'containers': containers,
    }

    return render(request, 'swarman/node_detail.html', context)



def create_swarm(request):
    '''Creates a New Swarm in Swarm Model'''

    swarm_name = request.GET.get('name', None)

    if swarm_name:
        # Check to see if swarm_name is currently in use
        s = Swarm.objects.filter(swarm_name=swarm_name).first()

        if not s:
            # If not in use, create a new swarm
            print(f"No Swarm with name {swarm_name} Found, creating now")
            try:
                Swarm.objects.create(swarm_name=swarm_name)
                return JsonResponse({'success': f'{swarm_name} created successfully'})
            except:
                return JsonResponse({'error': 'An error has occured'})

        else:
            # If in use, send error Code
            return JsonResponse({'error': f'{swarm_name} already in use'})
    else:
        return JsonResponse({'error': 'Swarm Name cannot be blank'})


class AddSwarm(View):
    '''
    Class View for adding new swarms to swarman
    '''

    template_name = 'swarman/new_swarm.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # If request contains 
        pass
