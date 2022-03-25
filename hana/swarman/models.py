from django.db import models

import requests
import json

# Create your models here.
class SwarmService(models.Model):

    name = models.CharField(max_length=32)


class Swarm(models.Model):
    """
    Swarm Model is for multiple swarm management. This is a feature that may be implemented at a future time
    """
    swarm_name = models.CharField(max_length=64)
    manager_join_token = models.CharField(max_length=200, blank=True, null=True)
    worker_join_token = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):

        return f'{self.swarm_name} - {self.node_count()} Node Swarm'

    def manager_join_command(self):
        '''Returns a String with the docker swarm join command and Manager Token'''
        return f'docker swarm join --token {self.manager_join_token}'

    def worker_join_command(self):
        '''Returns a String with the docker swarm join command and Worker Token'''
        return f'docker swarm join --token {self.worker_join_token}'

    def manager_nodes(self):
        '''Returns a QuerySet will all manager nodes assigned to a Swarm'''
        return self.nodes.filter(role='Manager').all()

    def worker_nodes(self):
        '''Returns a QuerySet with all worker nodes assigned to a Swarm'''
        return self.nodes.filter(role='Worker').all()

    def node_count(self):
        '''Returns a count of all nodes assigned to a swarm'''
        return len(self.nodes.all())

    def manager_count(self):
        '''Returns a count of all manager nodes assigned to a swarm'''
        return len(self.manager_nodes())

    def worker_count(self):
        '''Returns a count of all worker nodes assigned to a swarm'''
        return len(self.worker_nodes())

    def manager_ip_list(self):
        '''Return a list of Manager Addresses'''
        managers = self.manager_nodes()
        addresses = []
        for manager in managers:
            addresses.append(f'{manager.ip_address}:{manager.api_port}')

        return addresses


class Node(models.Model):
    """
    
    """
    hostname = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField(blank=True, null=True, unique=True)
    api_port = models.CharField(max_length=5)
    role = models.CharField(max_length=16)
    swarm = models.ForeignKey(Swarm, on_delete=models.CASCADE, related_name="nodes")
    docker_version_index = models.CharField(max_length=16)
    node_architecture = models.CharField(max_length=32)

    def __str__(self):
        return self.hostname

    def promote(self):
        '''
            Promotes a node from worker to manager
            docker API v1.41    
        '''
        if self.role == "Manager":
            return "Node is already a Manager"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():
                url = f'http://{address}/nodes/{self.hostname}/update?version={self.docker_version_index}'
                
                # post Request to swarm to promote Manager
                request_body = {
                    "Role": "manager"
                }
                # If Request is Successful - Update Role in database
                self.role = "Manager"
                self.save()
                return "Update Successful"

    def demote(self):
        '''
            Demotes a node from a manager to a worker
            docker API v1.41
        '''
        if self.role == "Worker":
            return "Node is already a Worker"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():
                url = f'http://{address}/nodes/{self.hostname}/update?version={self.docker_version_index}'
                
                # post Request to swarm to promote Manager
                request_body = {
                    "Role": "worker"
                }
                # If Request is Successful - Update Role in database
                self.role = "Worker"
                self.save()
                return "Update Successful"

    def get_node_info(self):
        '''
            Returns a JSON object with node information from Docker API
            docker API v1.41    
        '''

        # Get a list of all manager IPs, If a manager does not respond
        # Try the next manager
        for address in self.swarm.manager_ip_list():
            url = f'http://{address}/nodes/{self.hostname}'
            node_response = requests.get(url)

            if node_response.status_code == '200':
                node_data = node_response.text
                
                return json.loads(node_data)

            else:
                pass

        return None

    def get_cpu_load(self):
        '''
            Calculate the current CPU load on the node, returns value as a percentage
            docker API v1.41
        '''

        container_response = requests.get(f'http://{self.ip_address}:{self.api_port}/containers/json')
        container_json = json.loads(container_response.text)

        total_cpu_load = 0

        for container in container_json:
            id = container['Id']
            container_info = self.get_container_info(id)

            cpu_delta = container_info['cpu_stats']['cpu_usage']['total_usage'] - container_info['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = container_info['cpu_stats']['system_cpu_usage'] - container_info['precpu_stats']['system_cpu_usage']
            number_cpus = container_info['cpu_stats']['online_cpus']
            cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            total_cpu_load += cpu_usage

        return total_cpu_load


    def get_container_info(self, container_id):
        '''
            Get the container info from a node
            docker API v1.41    
        '''
        
        container_response = requests.get(f'http://{self.ip_address}:{self.api_port}/containers/{container_id}/stats?stream=0')
        container_json = json.loads(container_response)

        return container_json
        

    def get_memory_usage(self, container_id):
        '''
            Calculate Memory Usage on a Node, returns memory usage as percentage
            docker API v1.41
        '''
        # Check to see if node is armv71
        if self.node_architecture == "armv7l":
            return "Operation not supported on armv71 architecture"
        # Otherwise calculate memory usage on node
        else:

            container_response = requests.get(f'http://{self.ip_address}:{self.api_port}/containers/json')
            container_json = json.loads(container_response.text)

            total_memory_load = 0
            # Loop through all containers returned in container JSON
            # and calculate memory usage
            for container in container_json:

                id = container['Id']
                container_info = self.get_container_info(id)

                used_memory = container_info['memory_stats']['usage'] - container_info['memory_stats']['stats']['cache']
                available_memory = container_info['memory_stats']['limit']
                memory_usage = (used_memory / available_memory) * 100.0
                total_memory_load += memory_usage

            return total_memory_load

