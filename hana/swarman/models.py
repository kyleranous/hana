from django.db import models


# Create your models here.
class SwarmService(models.Model):

    name = models.CharField(max_length=32)


class ContainerImage(models.Model):

    name = models.CharField(max_length=200)
