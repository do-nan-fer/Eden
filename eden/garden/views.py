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

class PlantLogsView(APIView):
    def get(self, request, plant_ids, numback):
        # Splitting the plant_ids parameter into a list of integers
        plant_ids = [int(plant_id) for plant_id in plant_ids.split(',')]

        # Fetching data from Elasticsearch
        es_url = 'https://192.168.101.11:9200/garden-plants/_search'
        auth = ('admin', 'admin')
        headers = {'Content-Type': 'application/json'}
        query = {
            "size": numback,
            "sort": [{"timestamp": {"order": "desc"}}]  # Fetch most recent logs first
        }

        try:
            response = requests.post(es_url, auth=auth, headers=headers, json=query, verify=False)
            response.raise_for_status()
            data = response.json()

            print("PRINTING INITIAL DATA:")
            print(data)  # Printing the initial data before filtering

            self.filter_data(data, plant_ids)

            print("PRINTING FILTERED DATA:")
            print(data)  # Printing the filtered data

            # Reverse the order of hits to simulate a stack, newest at the bottom
            data['hits']['hits'] = data['hits']['hits'][::-1]

            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def filter_data(self, data, target_plant_ids):
        # Convert target_plant_ids to strings for consistent comparison
        target_plant_ids = [str(plant_id) for plant_id in target_plant_ids]

        for hit in data['hits']['hits']:
            filtered_responses = []
            for response in hit['_source']['responses']:
                # Getting the plant ID of each response
                response_plant_id = str(response.get('plant_id'))
                if response_plant_id in target_plant_ids:
                    filtered_responses.append(response)
            # Assigning the filtered responses back to the hit
            hit['_source']['responses'] = filtered_responses

class PackageLogsView(APIView):
    def get(self, request, package_ids, numback):
        # Splitting the package_ids parameter into a list of integers
        package_ids = [int(package_id) for package_id in package_ids.split(',')]
        
        # Fetching data from Elasticsearch
        es_url = 'https://192.168.101.11:9200/garden-packages/_search'
        auth = ('admin', 'admin')
        headers = {'Content-Type': 'application/json'}
        query = {
            "size": numback,
            "sort": [{"timestamp": {"order": "desc"}}],  # Fetch most recent logs first
            "query": {"match_all": {}}
        }

        try:
            response = requests.post(es_url, auth=auth, headers=headers, json=query, verify=False)
            response.raise_for_status()
            data = response.json()

            # Filtering process
            hits = data['hits']['hits']
            for hit in hits:
                packages = hit['_source'].get('packages', [])
                filtered_packages = [package for package in packages if package.get('package_id') in package_ids]
                hit['_source']['packages'] = filtered_packages
            
            # Debugging prints
            print(f"Filtered data based on package_ids {package_ids}:")
            for hit in hits:
                print(hit['_source']['packages'])

            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

