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
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='picks')
    api_field = models.CharField(max_length=100, help_text='Dot-notated path to the field in the API response, e.g., "main.temp" for {"main": {"temp": value}}.')
    condition_type = models.CharField(max_length=20, choices=(('gt', 'Greater Than'), ('lt', 'Less Than')), help_text='Type of condition to evaluate.')
    condition_value = models.FloatField(help_text='The value to compare the api_field against.')
    script = models.TextField(help_text='The script or action to trigger when the condition is met.')

    def get_value_by_path(self, data, path):
        """Navigate through nested dictionary using keys in path."""
        for key in path:
            data = data.get(key, None)
            if data is None:
                break
        return data

    def condition_met(self, field_value):
        """Check if the condition is met based on the type and value."""
        if self.condition_type == 'gt' and field_value > self.condition_value:
            return True
        elif self.condition_type == 'lt' and field_value < self.condition_value:
            return True

    def trigger_script(self):
        # Placeholder for script execution logic
        print(f"Triggering script for {self.plant.name}: {self.script}")
