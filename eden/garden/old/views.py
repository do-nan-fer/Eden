from rest_framework import generics
from .models import Plant, Pick
from .serializers import PlantSerializer, PickSerializer

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


class PickListAPIView(generics.ListAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickListByPlantAPIView(generics.ListAPIView):
    serializer_class = PickSerializer

    def get_queryset(self):
        """Filter picks by the provided plant ID."""
        plant_id = self.kwargs.get('plant_id')
        return Pick.objects.filter(plant__id=plant_id)

class PickCreateAPIView(generics.CreateAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer

class PickUpdateAPIView(generics.UpdateAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer



class PickDestroyAPIView(generics.DestroyAPIView):
    queryset = Pick.objects.all()
    serializer_class = PickSerializer
