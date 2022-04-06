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


class NodeUpdateSerializer(serializers.Serializer):
    """
    Serializer for sending Updates to a Node in a swarm
    """
    ROLE_CHOICES = (
        ("worker", "worker"),
        ("manager", "manager")
    )
    AVAIL_CHOICES = (
        ("available", "available"),
        ("pause", "pause"),
        ("drain", "drain")
    )
    availability = serializers.ChoiceField(choices=AVAIL_CHOICES)
    name = serializers.CharField(max_length=64, required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)
