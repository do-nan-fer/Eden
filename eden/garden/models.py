from django.db import models
from django.utils import timezone

class Plant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    collect = models.IntegerField(default=0, help_text='Set to 1 to collect data for this plant.')
    status = models.IntegerField(default=0, help_text='Current status of the plant (0 for inactive, 1 for active).')
    full_query_command = models.TextField(help_text='The full command to fetch data, including authentication and any flags.', default='')
    last_status_change = models.DateTimeField(default=timezone.now, help_text='Timestamp of the last status change.')

class Pick(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    api_fields = models.ManyToManyField('ApiField', related_name='picks')

class ApiField(models.Model):
    name = models.CharField(max_length=100)

class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    picks = models.ManyToManyField(Pick, related_name='packages')
   
    def count_unique_plants(self):
        # Utiliza un set para evitar duplicados y contar plantas únicas a través de los picks
        unique_plants = {pick.plant.id for pick in self.picks.all()}
        return len(unique_plants)

    def count_unique_api_fields(self):
        # Recopila todos los ApiField únicos a través de los picks
        unique_api_fields = set()
        for pick in self.picks.prefetch_related('api_fields').all():
            for field in pick.api_fields.all():
                unique_api_fields.add(field.id)
        return len(unique_api_fields)
