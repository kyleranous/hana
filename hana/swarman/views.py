from django.shortcuts import render
from django.http import HttpResponse

import requests
import json


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

    Enable API on Node:

    `sudo nano /lib/systemd/system/docker.service`
    Find Line 'ExecStart=...'
    Add 'cp://0.0.0.0:2375 -H' After 'usr/bin/dockerd -H'

    Restart Services
    'sudo systemctl daemon-reload'
    'sudo service docker restart'
    """
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

    container_response = requests.get(f'http://{ip_address}:2375/containers/json')
    container_data = container_response.text
    container_json = json.loads(container_data)

    container_stats = []
    total_cpu_usage = 0
    total_memory_usage = 0
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

        used_memory = resource_json['memory_stats']['usage'] - resource_json['memory_stats']['stats']['cache']
        available_memory = resource_json['memory_stats']['limit']
        memory_usage = (used_memory / available_memory) * 100.0
        total_memory_usage += memory_usage
        
        container_stats.append((container['Names'][0],
                                format(cpu_usage, '.2f'), 
                                format(memory_usage, '.2f')))
    
    context = {
        'labels': labels,
        'role': role,
        'availability': availability,
        'hostname': hostname,
        'architecture': architecture,
        'os': operating_system,
        'cores': int(cpu_cores),
        'memory': format(memory, '.3f'),
        'ip_address': ip_address,
        'total_cpu_usage': format(total_cpu_usage, '.2f'),
        'total_memory_usage': format(total_memory_usage, '.2f'),
        'container_stats': container_stats
    }

    return render(request, 'swarman/node_detail.html', context)