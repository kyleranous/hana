# Generated by Django 4.0.3 on 2022-03-25 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swarman', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='api_port',
            field=models.CharField(default=2375, max_length=5),
            preserve_default=False,
        ),
    ]
