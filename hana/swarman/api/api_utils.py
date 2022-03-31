from tempfile import TemporaryFile
from tkinter import N
import requests
import json


def get_existing_node_info(swarm_ip):
    try:
        url = f'http://{swarm_ip}/nodes?membership=accepted'
        node_response = requests.get(url)
    
        nodes_json = json.loads(node_response.text)
        parsed_nodes_json = {
            'nodes' : [],
        }
        for node in nodes_json:
            node_data = {
                'hostname' : node['Description']['Hostname'],
                'docker_version_index' : node['Version']['Index'],
                'node_architecture' : node['Description']['Platform']['Architecture'],
                'role' : node['Spec']['Role'].capitalize()
            }
            if node['Status']['Addr'] == '0.0.0.0':
                node_data['ip_address'] = node['ManagerStatus']['Addr'].split(':')[0]
            else:
                node_data['ip_address'] = node['Status']['Addr']
            parsed_nodes_json['nodes'].append(node_data)
        return parsed_nodes_json
    except:
        return {'error' : f'Error connecting to {url}'}
    

def get_swarm_tokens(swarm_ip):
    try:
        url = f'http://{swarm_ip}/swarm'
        swarm_response = requests.get(url)

        swarm_response = json.loads(swarm_response.text)

        return swarm_response["JoinTokens"]

    except:
        return {'error' : f'Error connecting to {url}'}