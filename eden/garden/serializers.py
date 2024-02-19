from rest_framework import serializers
from .models import Plant, ApiField, Pick, Package

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = '__all__'

class AvailablePlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'name', 'collect', 'status']

class ApiFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiField
        fields = ['id', 'name']

class PickSerializer(serializers.ModelSerializer):
    api_fields = ApiFieldSerializer(many=True, allow_null=True)

    class Meta:
        model = Pick
        fields = ['id', 'plant', 'api_fields']

    def create(self, validated_data):
        api_fields_data = validated_data.pop('api_fields')
        pick = Pick.objects.create(**validated_data)
        for api_field_data in api_fields_data:
            api_field, created = ApiField.objects.get_or_create(**api_field_data)
            pick.api_fields.add(api_field)
        return pick

    def update(self, instance, validated_data):
        api_fields_data = validated_data.pop('api_fields', [])
        instance.plant = validated_data.get('plant', instance.plant)
        instance.save()

        instance.api_fields.clear()
        for api_field_data in api_fields_data:
            api_field, created = ApiField.objects.get_or_create(**api_field_data)
            instance.api_fields.add(api_field)

        return instance

class PackageSerializer(serializers.ModelSerializer):
    picks = serializers.PrimaryKeyRelatedField(many=True, queryset=Pick.objects.all())
    unique_plants_count = serializers.SerializerMethodField()
    unique_api_fields_count = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ['id', 'name', 'description', 'picks', 'unique_plants_count', 'unique_api_fields_count']

    def get_unique_plants_count(self, obj):
        return obj.count_unique_plants()

    def get_unique_api_fields_count(self, obj):
        return obj.count_unique_api_fields()
