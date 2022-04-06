from rest_framework import serializers

from swarman.models import (
    Swarm,
    Node,
)


class SwarmSerializer(serializers.ModelSerializer):
    '''
    Serializer for handling Swarm Actions
    '''

    class Meta:
        model = Swarm
        fields = '__all__'

        read_only_fields = (
            'manager_join_token',
            'worker_join_token',
        )


class NodeSerializer(serializers.ModelSerializer):
    '''
    Serializer for handling Node Actions
    '''
    class Meta:
        model = Node
        fields = '__all__'
