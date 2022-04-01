from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

import requests
import json

from .models import Swarm


SWARM_MANAGER_URL = 'http://192.168.1.200:2375'

# Create your views here.
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

    try:
        node_response = requests.get(SWARM_MANAGER_URL + f'/nodes/{node_id}')
        node_data = node_response.text

        node_json = json.loads(node_data)
        
        labels = node_json['Spec']['Labels']
        role = node_json['Spec']['Role']
        availability = node_json['Spec']['Availability']
        hostname = node_json['Description']['Hostname']
        architecture = node_json['Description']['Platform']['Architecture']
        operating_system = node_json['Description']['Platform']['OS']
        cpu_cores = node_json['Description']['Resources']['NanoCPUs'] / (10**9)
        memory = node_json['Description']['Resources']['MemoryBytes'] / (10**9)
        ip_address = node_json['Status']['Addr']
        if ip_address == '0.0.0.0': # This is added for a bug with docker reporting some manager nodes IP as the default listen address
            ip_address = node_json['ManagerStatus']['Addr']
            ip_address = ip_address.split(':')[0]
        container_response = requests.get(f'http://{ip_address}:2375/containers/json')
        
        container_data = container_response.text
        container_json = json.loads(container_data)
        
        container_stats = []
        total_cpu_usage = 0
        total_memory_usage = 0
        
        context = {
            'labels': labels,
            'role': role,
            'availability': availability,
            'hostname': hostname,
            'architecture': architecture,
            'os': operating_system,
            'cores': int(cpu_cores),
            'memory': format(memory, '.3f'),
            'ip_address': ip_address
        }
        
        
        for container in container_json:
            
            id = container['Id']
            resource_response = requests.get(f'http://{ip_address}:2375/containers/{id}/stats?stream=0')
            resource_data = resource_response.text
            resource_json = json.loads(resource_data)
            
            cpu_delta = resource_json['cpu_stats']['cpu_usage']['total_usage'] - resource_json['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = resource_json['cpu_stats']['system_cpu_usage'] - resource_json['precpu_stats']['system_cpu_usage']
            number_cpus = resource_json['cpu_stats']['online_cpus']
            cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            total_cpu_usage += cpu_usage
            # Need to allow memory tracking on Raspberry Pi
            if architecture != 'armv7l':
                print(resource_json['memory_stats']['stats'])
                used_memory = resource_json['memory_stats']['usage'] - resource_json['memory_stats']['stats']['cache']
                print("Checkpoint 2")
                available_memory = resource_json['memory_stats']['limit']
            
                memory_usage = (used_memory / available_memory) * 100.0
                total_memory_usage += memory_usage
            else:
                memory_usage = 0
                total_memory_usage = 0
            
            container_stats.append((container['Names'][0],
                                    format(cpu_usage, '.2f'), 
                                    format(memory_usage, '.2f')))

            context['total_cpu_usage'] = format(total_cpu_usage, '.2f')
            context['total_memory_usage'] = format(total_memory_usage, '.2f')
        
        context['container_stats'] = container_stats
            
    except:
        context = {
            'error' : f'There was an error fetching data from {node_id}'
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
