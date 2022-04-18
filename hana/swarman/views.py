from django.shortcuts import (
    render,
    get_object_or_404
)
from django.http import JsonResponse
from django.views import View
from django.utils.html import format_html

import requests
import json
import docker

from .models import (
    Swarm,
    Node,
)


SWARM_MANAGER_URL = 'http://192.168.1.200:2375'

# Create your views here.


def swarm_dashboard(request, swarm_id):
    """
    Display information about a swarm. Includes node and service status
    """
    swarm = get_object_or_404(Swarm, id=swarm_id)
    nodes = swarm.nodes.order_by('hostname')

    services = []
    service_list = swarm.get_services()

    if "Error" not in service_list:
        for service in swarm.get_services():
            service_info = {
                'name': service['Spec']['Name'],
                'ID': service['ID'],
                'image': service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0],
                'replicas': service['Spec']['Mode']['Replicated']['Replicas'],
                'desired_tasks': service['ServiceStatus']['DesiredTasks'],
                'target_port': service['Endpoint']['Ports'][0]['TargetPort'],
                'published_port': service['Endpoint']['Ports'][0]['PublishedPort'],
            }
            tasks = swarm.get_service_tasks(service['ID'])
            service_info['replicas'] = 0
            for task in tasks:
                if task['Status']['State'] == "running":
                    service_info['replicas'] += 1

            services.append(service_info)

    else:
        services.append('ERROR')

    context = {
        "swarm": swarm,
        "nodes": nodes,
        "services": services,
    }
    # print(services)
    return render(request, 'swarman/swarm_dashboard.html', context)


def node_detail(request, node_id):
    """
    Displays Node Specific Details
    """
    # Get Node Object
    node = get_object_or_404(Node, id=node_id)

    # Get Container List
    try:
        client = docker.DockerClient(
            base_url=f'tcp://{node.ip_address}:{node.api_port}')
        containers = []
        for container in client.containers.list():
            containers.append(container.attrs)

    except:
        containers = [{"error": "Error retrieving containers"}]

    context = {
        'node': node,
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


def service_detail(request, swarm_id):

    if request.method == "GET":

        service_id = request.GET.get('service', None)
        context = {
            'swarm_id' : swarm_id,
        }
        swarm = get_object_or_404(Swarm, id=swarm_id)
        if service_id:
            service = swarm.get_service_data(service_id)
            tasks = swarm.get_service_tasks(service_id)
            context['running_tasks'] = 0
            for task in tasks:
                if task['Status']['State'] == "running":
                    context['running_tasks'] += 1
            
            context['service_name'] = service['Spec']['Name']
            context['service_id'] = service['ID']
            context['replicas'] = service['Spec']['Mode']['Replicated']['Replicas']
            context['image'] = service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0]
            context['published_port'] = service['Spec']['EndpointSpec']['Ports'][0]['PublishedPort']
            context['target_port'] = service['Spec']['EndpointSpec']['Ports'][0]['TargetPort']
            # Calculate Service Status
            if context['running_tasks'] == 0 and context['replicas'] == 0:
                context['service_status'] = 'Paused'
                context['service_status_display'] = format_html('<strong><span class="pause">{}</span></strong>',
                                                        'Paused')  
            elif 0 < context['running_tasks'] < context['replicas']:
                context['service_status'] = 'Degraded'
                context['service_status_display'] = format_html('<strong><span class="degraded">{}</span></strong>',
                                                        'Degraded')
            elif 0 == context['running_tasks'] < context['replicas']:
                context['service_status'] = 'Error'
                context['service_status_display'] = format_html('<strong><span class="error">{}</span></strong>',
                                                        'Error')
            else:
                context['service_status'] = 'Running'
                context['service_status_display'] = format_html('<strong><span class="running">{}</span></strong>',
                                                        'Running')
            
            
        else:
            context['error'] = 'Service ID is a required URL parameter'

        return render(request, 'swarman/service_detail.html', context)