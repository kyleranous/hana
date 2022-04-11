from swarman.models import Swarm


def swarm_list(request):
    return {'swarm_list': Swarm.objects.all()}