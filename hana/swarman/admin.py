from django.contrib import admin

from .models import Swarm, Node


# Register your models here.
admin.site.register(Swarm)
admin.site.register(Node)