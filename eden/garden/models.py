from django.db import models

class Plant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    collect = models.IntegerField(default=0, help_text='Set to 1 to collect data for this plant.')
    status = models.IntegerField(default=0, help_text='Current status of the plant (0 for inactive, 1 for active).')
    full_query_command = models.TextField(help_text='The full command to fetch data, including authentication and any flags.', default='')

class Pick(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    api_fields = models.ManyToManyField('ApiField', related_name='picks')

class ApiField(models.Model):
    name = models.CharField(max_length=100)

class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    picks = models.ManyToManyField(Pick, related_name='packages')

