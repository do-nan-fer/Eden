from django.db import models

class Plant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    collect = models.IntegerField(default=0, help_text='Set to 1 to collect data for this plant.')
    status = models.IntegerField(default=0)
    api_endpoint = models.URLField(help_text='The base URL for the API endpoint.', default='http://example.com')
    api_method = models.CharField(max_length=10, default='GET', help_text='The HTTP method (e.g., GET, POST).')
    api_auth_type = models.CharField(max_length=50, blank=True, null=True, help_text='The type of authentication (e.g., Token, Basic).', default='')
    api_auth_key = models.CharField(max_length=255, blank=True, null=True, help_text='The authentication key or token.', default='')
    api_param_name = models.CharField(max_length=100, blank=True, null=True, help_text='The name of the primary query parameter.', default='')
    api_param_value = models.CharField(max_length=255, blank=True, null=True, help_text='The value of the primary query parameter.', default='')

class Pick(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    api_fields = models.ManyToManyField('ApiField', related_name='picks')

class ApiField(models.Model):
    name = models.CharField(max_length=100)

class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    picks = models.ManyToManyField(Pick, related_name='packages')

