# Generated by Django 4.0.3 on 2022-03-25 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swarman', '0002_node_api_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='docker_version_index',
            field=models.CharField(default=373531, max_length=16),
            preserve_default=False,
        ),
    ]
