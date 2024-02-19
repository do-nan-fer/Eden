from django.urls import path
from .views import (
    PlantListAPIView, PlantDetailView, PlantCreateAPIView, PlantUpdateAPIView, PlantDestroyAPIView, AvailablePlantsAPIView, PlantDataView, PlantLogsView,
    PickListView, PickCreateView, PickDetailView, PickUpdateView, PickDestroyView,
    PackageListView, PackageCreateView, PackageDetailView, PackageUpdateView, PackageDestroyView, PackageLogsView
)

urlpatterns = [
    path('plants/', PlantListAPIView.as_view(), name='plant-list'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('plants/add/', PlantCreateAPIView.as_view(), name='plant-add'),
    path('plants/<int:pk>/update/', PlantUpdateAPIView.as_view(), name='plant-update'),
    path('plants/<int:pk>/delete/', PlantDestroyAPIView.as_view(), name='plant-delete'),
    path('plants/available/', AvailablePlantsAPIView.as_view(), name='available-plants'),
    path('plants/<int:plant_id>/data/', PlantDataView.as_view(), name='plant-data'),
    path('plants/logs/<str:plant_ids>/<int:numback>/', PlantLogsView.as_view(), name='plant-logs'),

    path('picks/', PickListView.as_view(), name='pick-list'),
    path('picks/add/', PickCreateView.as_view(), name='pick-create'),
    path('picks/<int:pk>/', PickDetailView.as_view(), name='pick-detail'),
    path('picks/<int:pk>/update/', PickUpdateView.as_view(), name='pick-update'),
    path('picks/<int:pk>/delete/', PickDestroyView.as_view(), name='pick-delete'),

    path('packages/', PackageListView.as_view(), name='package-list'),
    path('packages/add/', PackageCreateView.as_view(), name='package-create'),
    path('packages/<int:pk>/', PackageDetailView.as_view(), name='package-detail'),
    path('packages/<int:pk>/update/', PackageUpdateView.as_view(), name='package-update'),
    path('packages/<int:pk>/delete/', PackageDestroyView.as_view(), name='package-delete'),
    path('packages/logs/<str:package_ids>/<int:numback>/', PackageLogsView.as_view(), name='package-logs'),
]

