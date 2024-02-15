from rest_framework import generics
from rest_framework.response import Response
from .models import Plant, Pick, Package
from .serializers import PlantSerializer, AvailablePlantSerializer, PickSerializer, PackageSerializer

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
        # Filter plants with status 1
        return Plant.objects.filter(status=1)

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

