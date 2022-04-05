from django.db import models
from django.utils.html import format_html

import requests
import json
import docker
import time


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

    def get_services(self):
        '''
        Return a list of services running on a swarm
        '''
        for ip_address in self.manager_ip_list():
            #client = docker.DockerClient(base_url=f'tcp://{ip_address}')
            url = f'http://{ip_address}/services?status=true'
            response = requests.get(url)

            if response.status_code == 200:
                service_list = response.json
                services = []

                for service in service_list():
                    services.append(service)

                return services

    @property
    def services_count(self):
        '''
        Return a count of services running on a swarm
        '''
        return len(self.get_services())

class Node(models.Model):
    """
    
    """
    hostname = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField(blank=True, null=True, unique=True)
    api_port = models.CharField(max_length=5)
    role = models.CharField(max_length=16)
    swarm = models.ForeignKey(Swarm, null=True, on_delete=models.CASCADE, related_name="nodes")
    docker_version_index = models.CharField(max_length=16)
    node_architecture = models.CharField(max_length=32)
    node_id = models.CharField(max_length=200)
    total_memory = models.FloatField(default = 0)
    cpu_count = models.IntegerField(default = 0)
    os = models.CharField(max_length = 32, default="Unknown")
    docker_engine = models.CharField(max_length=16, default="Unknown")

    def __str__(self):
        return self.hostname

    def promote(self):
        '''
            Promotes a node from worker to manager
        '''

        # TODO:
        # - Adjust Unit Test to retrieve mock swarm data for demote function

        if self.role == "Manager":
            return "Node is already a Manager"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():

                client = docker.DockerClient(base_url=f'tcp://{address}')

                node = client.nodes.get(self.hostname)
                # post Request to swarm to promote Manager
                node_spec = {
                    "Role": "manager",
                    "Availability": "active"
                }

                if node.update(node_spec):
                    self.role = "Manager"
                    self.save()
                    client.close()
                    return True

            return False

    def demote(self):
        '''
            Demotes a node from a manager to a worker
        '''
        # TODO:
        # - Adjust Unit Test to retrieve mock swarm data for demote function

        if self.role == "Worker":
            return "Node is already a Worker"

        else:
            # Attempt to update, if communication fails,
            # Go to the next manager in the list
            for address in self.swarm.manager_ip_list():
                client = docker.DockerClient(base_url=f'tcp://{address}')

                node = client.nodes.get(self.hostname)
                # post Request to swarm to promote Manager
                node_spec = {
                    "Role": "worker",
                    "Availability": "active"
                }

                if node.update(node_spec):
                    self.role = "Worker"
                    self.save()
                    client.close()
                    return True

            return False 
                

    def get_node_info(self):
        '''
            Returns a JSON object with node information from Docker API   
        '''

        for address in self.swarm.manager_ip_list():
            
            try:
                client = docker.DockerClient(base_url=f'tcp://{address}')

                node_data = client.nodes.get(self.hostname).attrs
                client.close()
                return node_data

            except Exception as err: 
                pass

        return err

    @property
    def get_cpu_load(self):
        '''
            Calculate the current CPU load on the node, returns value as a percentage
            Returns float
        '''

        client = docker.DockerClient(base_url=f'tcp://{self.ip_address}:{self.api_port}')
        total_cpu_load = 0

        for container in client.containers.list():
            
            container_info = container.stats(stream=False)
            cpu_delta = container_info['cpu_stats']['cpu_usage']['total_usage'] - container_info['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = container_info['cpu_stats']['system_cpu_usage'] - container_info['precpu_stats']['system_cpu_usage']
            number_cpus = container_info['cpu_stats']['online_cpus']
            cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            total_cpu_load += cpu_usage

        client.close()
        return float(format(total_cpu_load, '.2f'))


    def get_container_info(self, container_id):
        '''
            Get the container info from a node
        '''
        client = docker.DockerClient(base_url=f'tcp://{self.ip_address}:{self.api_port}')

        return client.services.get(container_id).attrs
        
    @property
    def get_memory_usage(self):
        '''
            Calculate Memory Usage on a Node, returns memory usage as percentage
            Returns Float
        '''
        client = docker.DockerClient(base_url=f'tcp://{self.ip_address}:{self.api_port}')

        total_memory_load = 0
        # Loop through all containers returned in container JSON
        # and calculate memory usage
        for container in client.containers.list():

            container_info = container.stats(stream=False)

            used_memory = container_info['memory_stats']['usage']
            available_memory = container_info['memory_stats']['limit']
            memory_usage = (used_memory / available_memory) * 100.0
            total_memory_load += memory_usage
        
        client.close()
        return float(format(total_memory_load, '.2f'))
        
    @property
    def get_status(self):

        return self.get_node_info()['Status']['State']

    @property
    def get_availability(self):
        # THIS NEEDS TO BE REMOVED BEFORE PUSH
        return 'active'
        try:
            result = self.get_node_info()['Spec']['Availability']
            return result
        except:
            return 'Error'

    @property
    def utilization(self):
        """
        Calculates the total CPU and memory utalization by services on the node as a percentage.
        Returns a Tupple (cpu_utilization, memory_utilization)
        """
        client = docker.DockerClient(base_url=f'tcp://{self.ip_address}:{self.api_port}')

        total_memory_load = 0
        total_cpu_load = 0
        # Loop through all containers returned in container JSON
        # and calculate memory and cpu usage
        
        for container in client.containers.list():

            container_info = container.stats(stream=False)
            # Calculate Memory Usage per container   
            used_memory = container_info['memory_stats']['usage']
            available_memory = container_info['memory_stats']['limit']
            memory_usage = (used_memory / available_memory) * 100.0
            
            total_memory_load += memory_usage

            #Calculate CPU Usage per container
            cpu_delta = container_info['cpu_stats']['cpu_usage']['total_usage'] - container_info['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = container_info['cpu_stats']['system_cpu_usage'] - container_info['precpu_stats']['system_cpu_usage']
            number_cpus = container_info['cpu_stats']['online_cpus']
            cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            total_cpu_load += cpu_usage
        

        client.close()
        utilization = (float(format(total_cpu_load, '.2f')), float(format(total_memory_load, '.2f')))
        return utilization

    @property
    def utilization_display(self):
        try:
            result = self.utilization
        
            return format_html("{}<br>{}",
                               f"CPU: {result[0]}%",
                               f"Memory: {result[1]}%")
        except:
            return "Error retreiving node utilization stats"
                         
    def leave_swarm(self):
        client = docker.DockerClient(base_url=f"tcp://{self.ip_address}:{self.api_port}")

        if client.swarm.leave():
            self.swarm = None
            self.role = "NO SWARM"
            self.save()
            return True

        return False

    
    def utilization_per_container(self):
        """
        Calculates the total CPU and memory utalization by containers on the node as a percentage.
        Returns a list of dictionaries with container name, cpu, and memory utilization
        """
        client = docker.DockerClient(base_url=f'tcp://{self.ip_address}:{self.api_port}')

        
        # Loop through all containers returned in container JSON
        # and calculate memory and cpu usage
        utilization_data = []
        for container in client.containers.list():
            container_utilization = {}
            container_info = container.stats(stream=False)
            container_utilization['name'] = container.attrs['Name'][0]

            # Calculate Memory Usage per container   
            used_memory = container_info['memory_stats']['usage']
            available_memory = container_info['memory_stats']['limit']
            memory_usage = (used_memory / available_memory) * 100.0
            container_utilization['memory'] = float(format(memory_usage, '.2f'))
            

            #Calculate CPU Usage per container
            cpu_delta = container_info['cpu_stats']['cpu_usage']['total_usage'] - container_info['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = container_info['cpu_stats']['system_cpu_usage'] - container_info['precpu_stats']['system_cpu_usage']
            number_cpus = container_info['cpu_stats']['online_cpus']
            cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            container_utilization['cpu'] = float(format(cpu_usage, '.2f'))
            utilization_data.append(container_utilization)

        client.close()
       
        return utilization_data
class Service(models.Model):

    service_name = models.CharField(max_length=64)
    service_id = models.CharField(max_length=64)
    swarm = models.ForeignKey(Swarm, on_delete=models.CASCADE)
    target_port = models.IntegerField()
    published_port = models.IntegerField()
    desired_replicas = models.IntegerField()
    image_name = models.CharField(max_length=64)
    status = models.CharField(max_length=64)


class Mounts(models.Model):

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    mount_type = models.CharField(max_length=32)
    mount_src = models.CharField(max_length=200)
    mount_target = models.CharField(max_length=200)