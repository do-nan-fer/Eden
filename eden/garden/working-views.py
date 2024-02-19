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
    def get(self, request, plant_id, numback):
        es_url = 'https://192.168.101.11:9200/garden-plants/_search'
        auth = ('admin', 'admin')  # Reminder to use actual credentials
        headers = {'Content-Type': 'application/json'}
        query = {
            "size": numback,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        try:
            response = requests.post(es_url, auth=auth, headers=headers, json=query, verify=False)
            response.raise_for_status()
            data = response.json()

            print("PRINTING INITIAL DATA:")
            print(data)  # Printing the initial data before filtering

            self.filter_data(data, plant_id)

            print("PRINTING FILTERED DATA:")
            print(data)  # Printing the data after filtering

            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def filter_data(self, data, target_plant_id):
        # Convert target_plant_id to string to ensure consistent comparison
        target_plant_id = str(target_plant_id)
        
        for hit in data['hits']['hits']:
            # Printing the target plant ID
            print("TARGET PLANT ID:", target_plant_id)
        
            for response in hit['_source']['responses']:
                # Getting the plant ID of each response
                response_plant_id = response.get('plant_id')
                # Convert response plant ID to string for consistent comparison
                response_plant_id = str(response_plant_id)
                # Printing the response plant ID
                print("RESPONSE PLANT ID:", response_plant_id)
            
                # Comparing the target plant ID with the response plant ID
                if response_plant_id == target_plant_id:
                    print(f"Comparison Result: {target_plant_id} == {response_plant_id}")
                else:
                    print(f"Comparison Result: {target_plant_id} != {response_plant_id}")
        
            # Filtering out only the response objects with matching plant_id
            filtered_responses = [response for response in hit['_source']['responses'] if str(response.get('plant_id')) == target_plant_id]
        
            # Assigning the filtered responses back to the hit
            hit['_source']['responses'] = filtered_responses
        
            # Printing the filtered responses
            print("FILTERED", filtered_responses)

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

