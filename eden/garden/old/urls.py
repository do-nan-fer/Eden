from django.urls import path
from .views import (PlantListAPIView, PlantDetailView, PlantCreateAPIView, PlantUpdateAPIView, PlantDestroyAPIView,
                    PickListAPIView, PickListByPlantAPIView, PickCreateAPIView, PickUpdateAPIView, PickDestroyAPIView)

urlpatterns = [
    path('plants/', PlantListAPIView.as_view(), name='plant-list'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('plants/add/', PlantCreateAPIView.as_view(), name='plant-add'),
    path('plants/<int:pk>/update/', PlantUpdateAPIView.as_view(), name='plant-update'),
    path('plants/<int:pk>/delete/', PlantDestroyAPIView.as_view(), name='plant-delete'),
    path('picks/', PickListAPIView.as_view(), name='pick-list'),
    path('picks/by-plant/<int:plant_id>/', PickListByPlantAPIView.as_view(), name='pick-list-by-plant'),
    path('picks/add/', PickCreateAPIView.as_view(), name='pick-add'),
    path('picks/<int:pk>/update/', PickUpdateAPIView.as_view(), name='pick-update'),
    path('picks/<int:pk>/delete/', PickDestroyAPIView.as_view(), name='pick-delete'),
]

