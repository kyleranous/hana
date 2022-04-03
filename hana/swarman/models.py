from django.db import models

import requests
import json


# Create your models here.
class Swarm(models.Model):
    """
    Swarm Model is for multiple swarm management. This is a feature that may be implemented at a future time
    """
    swarm_name = models.CharField(max_length=64, unique=True)
    manager_join_token = models.CharField(max_length=200, blank=True, null=True)
    worker_join_token = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):

        return f'{self.swarm_name} - {self.node_count} Node Swarm'

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

    @property
    def node_count(self):
        '''Returns a count of all nodes assigned to a swarm'''
        return len(self.nodes.all())

    @property
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
    node_id = models.CharField(max_length=200)

    def __str__(self):
        return self.hostname

    def promote(self):
        '''
            Promotes a node from worker to manager
            docker API v1.41    
        '''

        # TODO:
        # - Clean up this section to only have 1 return statement
        # - Adjust Unit Test to retrieve mock swarm data for demote function

        if self.role == "Manager":
            return "Node is already a Manager"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():
                url = f'http://{address}/nodes/{self.node_id}/update?version={self.get_version()}'
                
                # post Request to swarm to promote Manager
                request_body = {
                    "Role": "manager",
                    "Availability": "active"
                }

                response = requests.post(url, json=request_body)

                # If Request is Successful - Update Role in database
                if response.status_code == 200:
                    version = self.get_node_info()
                    self.role = "Manager"
                    self.docker_version_index = version['Version']['Index']
                    self.save()
                    return "Update Successful"
                elif response.status_code == 400:
                    return "Bad Parameter"
                elif response.status_code == 404:
                    return "No Such Node"
                elif response.status_code == 500:
                    return "Server Error"
                elif response.status_code == 503:
                    return "Node is not part of a swarm"
                else:
                    return "Promoting node failed for an unknown reason"

    def demote(self):
        '''
            Demotes a node from a manager to a worker
            docker API v1.41
        '''
        # TODO:
        # - Clean up this section to only have 1 return statement
        # - Adjust Unit Test to retrieve mock swarm data for demote function

        if self.role == "Worker":
            return "Node is already a Worker"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():
                url = f'http://{address}/nodes/{self.node_id}/update?version={self.get_version()}'
                
                # post Request to swarm to promote Manager
                request_body = {
                    "Role": "worker",
                    "Availability": "active"
                }

                response = requests.post(url, json=request_body)

                # If Request is Successful - Update Role in database
                if response.status_code == 200:
                    self.role = "Worker"
                    self.save()
                    return "Update Successful"
                elif response.status_code == 400:
                    return "Bad Parameter"
                elif response.status_code == 404:
                    return "No Such Node"
                elif response.status_code == 500:
                    return "Server Error"
                elif response.status_code == 503:
                    return "Node is not part of a swarm"
                else:
                    return "Demoting node failed for an unknown reason"

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
            
            if node_response.status_code == 200:
                node_data = node_response.text
                
                return json.loads(node_data)

            else:
                pass

        return None

    @property
    def get_cpu_load(self):
        '''
            Calculate the current CPU load on the node, returns value as a percentage
            Returns float
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

        return float(format(total_cpu_load, '.2f'))


    def get_container_info(self, container_id):
        '''
            Get the container info from a node
            docker API v1.41    
        '''
        
        container_response = requests.get(f'http://{self.ip_address}:{self.api_port}/containers/{container_id}/stats?stream=0')
        container_json = json.loads(container_response.text)

        return container_json
        

    @property
    def get_memory_usage(self):
        '''
            Calculate Memory Usage on a Node, returns memory usage as percentage
            Returns Float
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

            return float(format(total_memory_load, '.2f'))

    @property
    def get_version(self):
        '''
            Returns the Version Index of a node
            docker API v1.41    
        '''
        
        # Get a list of all manager IPs, If a manager does not respond
        # Try the next manager
        for address in self.swarm.manager_ip_list():
            url = f'http://{address}/nodes/{self.hostname}'
            node_response = requests.get(url)
            
            if node_response.status_code == 200:
                node_data = json.loads(node_response.text)
                
                return node_data['Version']['Index']

            else:
                pass

        return None
        
    @property
    def get_status(self):

        return self.get_node_info()['Status']['State']


class Service(models.Model):

    service_name = models.CharField(max_length=64)
    service_id = models.CharField(max_length=64)
    swarm = models.ForeignKey(Swarm, on_delete=models.CASCADE)
    target_port = models.IntegerField()
    published_port = models.IntegerField()
    desired_replicas = models.IntegerField()
    image_name = models.CharField(max_length=64)
    status = models.CharField()


class Mounts(models.Model):

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    mount_type = models.CharField(max_length=32)
    mount_src = models.CharField(max_length=200)
    mount_target = models.CharField(max_length=200)