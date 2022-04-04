from tempfile import TemporaryFile
from tkinter import N
import requests
import json
import docker


def get_existing_node_info(swarm_ip):

    try:
        client = docker.DockerClient(base_url=f'tcp://{swarm_ip}')

        parsed_nodes_json = {
            'nodes' : [],
        }
        for node in client.nodes.list():
            node_data = {
                'hostname' : node.attrs['Description']['Hostname'],
                'docker_version_index' : node.attrs['Version']['Index'],
                'node_architecture' : node.attrs['Description']['Platform']['Architecture'],
                'role' : node.attrs['Spec']['Role'].capitalize(),
                'node_id' : node.attrs['ID']
            }
            if node.attrs['Status']['Addr'] == '0.0.0.0':
                node_data['ip_address'] = node.attrs['ManagerStatus']['Addr'].split(':')[0]
            else:
                node_data['ip_address'] = node.attrs['Status']['Addr']
            parsed_nodes_json['nodes'].append(node_data)

        client.close()

        return parsed_nodes_json
    except:
        return {'error' : f'Error connecting to {swarm_ip}'}
    

def get_swarm_tokens(swarm_ip):

    client = docker.DockerClient(base_url=f'tcp://{swarm_ip}')
    join_tokens = client.swarm.attrs['JoinTokens']
    client.close()

    return join_tokens
    