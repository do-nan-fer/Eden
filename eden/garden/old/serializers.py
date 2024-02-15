from rest_framework import serializers
from .models import Plant, Pick

class PickSerializer(serializers.ModelSerializer):
    plant_name = serializers.SerializerMethodField()

    class Meta:
        model = Pick
        fields = '__all__'  # Ensure 'plant_name' is included

    def get_plant_name(self, obj):
        return obj.plant.name

class PlantSerializer(serializers.ModelSerializer):
    picks_count = serializers.SerializerMethodField()  # Add a method field for the count

    class Meta:
        model = Plant
        fields = '__all__'  # Ensure 'picks_count' is included if specifying fields explicitly

    def get_picks_count(self, obj):
        return obj.picks.count()  # Return the count of related picks
