from django.test import TestCase

from .models import (
    Swarm,
    Node,
)


# Create your tests here.
class SwarmModelTests(TestCase):

    def setUp(self):
        self.swarm = Swarm.objects.create(swarm_name="Test Swarm",
                                          manager_join_token="TEst-MaNgEr-ToKeN",
                                          worker_join_token="TEst-WoRkEr-ToKeN")
        self.node1 = Node.objects.create(hostname="testnode1",
                                         ip_address="0.0.0.0",
                                         api_port="2375",
                                         role="Manager", swarm=self.swarm)
        self.node2 = Node.objects.create(hostname="testnode2",
                                         ip_address="0.0.0.1",
                                         api_port="2375",
                                         role="Manager", swarm=self.swarm)
        self.node3 = Node.objects.create(hostname="testnode3",
                                         ip_address="0.0.0.2",
                                         api_port="2375",
                                         role="Worker", swarm=self.swarm)
        self.node4 = Node.objects.create(hostname="testnode4",
                                         ip_address="0.0.0.3",
                                         api_port="2375",
                                         role="Worker", swarm=self.swarm)

    def test_swarm_join_token_commands(self):
        '''Test that swarm returns correct docker join commands for worker and manager'''
        self.assertEqual(self.swarm.manager_join_command(),
                         'docker swarm join --token TEst-MaNgEr-ToKeN')
        self.assertEqual(self.swarm.worker_join_command(),
                         'docker swarm join --token TEst-WoRkEr-ToKeN')

    def test_swarm_manager_nodes(self):
        '''Test that manager_nodes() returns all manager nodes belonging to a swarm'''
        self.assertEqual(list(self.swarm.manager_nodes()),
                         [self.node1, self.node2])

    def test_swarm_worker_nodes(self):
        '''Test that worker_nodes() returns all worker nodes belonging to a swarm'''
        self.assertEqual(list(self.swarm.worker_nodes()),
                         [self.node3, self.node4])

    def test_swarm_node_count(self):
        '''Test that node_count returns a count of all Nodes in a swarm'''
        self.assertEqual(self.swarm.node_count(), 4)

    def test_swarm_node_manager_count(self):
        '''Test the manager_count() returns a count of all Manager Nodes in a swarm'''
        self.assertEqual(self.swarm.manager_count(), 2)

    def test_swarm_node_worker_count(self):
        '''Test the worker_count() returns a count of all Manager Nodes in a Swarm'''
        self.assertEqual(self.swarm.worker_count(), 2)

    def test_manager_ip_list(self):
        '''
            Test that manager_ip_list returns a formatted [IP ADDRESS]:[PORT] list of 
            all managers assigned to the swarm
        '''
        address_list = [
            f'{self.node1.ip_address}:{self.node1.api_port}',
            f'{self.node2.ip_address}:{self.node2.api_port}'
        ]

        self.assertEqual(self.swarm.manager_ip_list(), address_list)


class NodeModelTests(TestCase):

    def setUp(self):
        self.swarm = Swarm.objects.create(swarm_name="Test Swarm",
                                          manager_join_token="TEst-MaNgEr-ToKeN",
                                          worker_join_token="TEst-WoRkEr-ToKeN")
        self.node1 = Node.objects.create(hostname="testnode1",
                                         ip_address="0.0.0.0",
                                         api_port="2375",
                                         role="Manager", swarm=self.swarm)
        self.node2 = Node.objects.create(hostname="testnode2",
                                         ip_address="0.0.0.1",
                                         api_port="2375",
                                         role="Manager", swarm=self.swarm)
        self.node3 = Node.objects.create(hostname="testnode3",
                                         ip_address="0.0.0.2",
                                         api_port="2375",
                                         role="Worker", swarm=self.swarm)
        self.node4 = Node.objects.create(hostname="testnode4",
                                         ip_address="0.0.0.3",
                                         api_port="2375",
                                         role="Worker", swarm=self.swarm)

    def test_node_promote(self):
        '''Test that test_node_promote() will successfully Promote a worker to a manager'''
        self.assertEqual(self.node1.promote(), "Node is already a Manager")
        self.assertEqual(self.node3.promote(), "Update Successful")
        self.assertEqual(self.node3.role, "Manager")

    def test_node_demote(self):
        '''Test that test_node_demote() will successfully demote a manager to a worker'''
        self.assertEqual(self.node3.demote(), "Node is already a Worker")
        self.assertEqual(self.node1.demote(), "Update Successful")
        self.assertEqual(self.node1.role, "Worker")
