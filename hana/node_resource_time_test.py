"""
Script to test the ammount of time it takes to collect resource usage stats on a node
"""

import time

from swarman.models import Node

# Setup

# Get list of nodes with services running to test
nodes = Node.objects.all()
test_nodes = []
for node in nodes:

    if node.get_container_info() is not None:
        test_nodes.append(node)


# Test current Method with 2 functions and 2 API Calls
start = time.time()
for node in test_nodes:
    node.get_cpu_load
    node.get_memory_usage

end = time.time()
old_time_total = end - start
old_time_node_average = old_time_total / len(test_nodes)

# Test New Method with 1 function and 1 API Call
start = time.time()
for node in test_nodes:
    node.utilization

end = time.time()
new_time_total = end - start
new_time_node_average = new_time_total / len(test_nodes)

print('**********RUN REPORT**********')
print('\n')
print('Split Functions:')
print(f'Total Time for {len(test_nodes)} Nodes: {old_time_total}s')
print(f'Average Time: {old_time_node_average}s / Node')
print('\n')
print('Combined Function:')
print(f'Total Time for {len(test_nodes)} Nodes: {new_time_total}s')
print(f'Average Time: {new_time_node_average}s / Node')