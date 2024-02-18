from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import requests
from .models import Plant, Pick, Package
from .serializers import PlantSerializer, AvailablePlantSerializer, PickSerializer, PackageSerializer
import subprocess
from .tasks import update_plant_status  # Import the task
import json

class PlantListAPIView(generics.ListAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

class PlantDetailView(generics.RetrieveAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

class PlantCreateAPIView(generics.CreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

class PlantUpdateAPIView(generics.UpdateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

class PlantDestroyAPIView(generics.DestroyAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

class AvailablePlantsAPIView(generics.ListAPIView):
    serializer_class = AvailablePlantSerializer

    def get_queryset(self):
        queryset = Plant.objects.all()

        for plant in queryset:
            # Call the Celery task asynchronously
            update_plant_status.delay(plant.id)

        return queryset

class PlantDataView(APIView):
    def get(self, request, plant_id):
        es_url = 'https://192.168.101.11:9200/garden-plants/_search'
        auth = ('admin', 'admin')  # Update with actual credentials
        headers = {'Content-Type': 'application/json'}
        query = {
            "size": 1,
            "sort": [{"timestamp": {"order": "desc"}}],
            "query": {
                "match": {"responses.plant_id": plant_id}
            }
        }

        try:
            response = requests.post(es_url, auth=auth, headers=headers, json=query, verify=False)
            response.raise_for_status()
            data = response.json()

            formatted_data = {}
            for hit in data['hits']['hits']:
                for response in hit['_source']['responses']:
                    if response['plant_id'] == str(plant_id):
                        formatted_data = self.format_nested_data(response, parent_key='')

            if formatted_data:
                return Response(formatted_data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No specific data found for plant ID in the latest document."}, status=status.HTTP_404_NOT_FOUND)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def format_nested_data(self, data, parent_key=''):
        formatted = {}
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                formatted.update(self.format_nested_data(value, parent_key=full_key))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                full_key = f"{parent_key}[{idx}]"
                formatted.update(self.format_nested_data(item, parent_key=full_key))
        else:
            formatted[parent_key] = data
        return formatted

class PlantLogsView(APIView):
    def get(self, request, plant_id, numback):
        es_url = 'https://192.168.101.11:9200/garden-plants/_search'
        auth = ('admin', 'admin')  # Update with actual credentials
        headers = {'Content-Type': 'application/json'}
        query = {
            "size": numback,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        try:
            response = requests.post(es_url, auth=auth, headers=headers, json=query, verify=False)
            response.raise_for_status()
            data = response.json()

            # Print the entire data received
            print("PRINTING DATA", data)

            # Filter out data for the specified plant ID
            filtered_data = []
            for hit in data.get('hits', {}).get('hits', []):
                source = hit.get('_source', {})
                # Check if plant_id in any of the responses matches the given plant_id
                if any(response.get('plant_id') == plant_id for response in source.get('responses', [])):
                    filtered_data.append(source)
                    print("Data for Plant ID", plant_id, "included.")

            # Print the filtered data
            print("Filtered Data:", filtered_data)

            return Response(filtered_data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PickListView(generics.ListAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickCreateView(generics.CreateAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickDetailView(generics.RetrieveAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickUpdateView(generics.UpdateAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickDestroyView(generics.DestroyAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PackageListView(generics.ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

class PackageCreateView(generics.CreateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

class PackageDetailView(generics.RetrieveAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

class PackageUpdateView(generics.UpdateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

class PackageDestroyView(generics.DestroyAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    http_method_names = ['delete']

