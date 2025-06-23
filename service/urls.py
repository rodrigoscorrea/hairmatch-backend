from django.urls import path
from .views import ListService, ListServiceHairdresser, CreateService, RemoveService, UpdateService
urlpatterns = [
    path('create', CreateService.as_view(), name='create_service'),
    path('list/<int:service_id>', ListService.as_view(), name='list_service'),
    path('list', ListService.as_view(), name='list_service'),
    path('hairdresser/<int:hairdresser_id>', ListServiceHairdresser.as_view(), name='list_service_hairdresser'),
    path('update/<int:service_id>', UpdateService.as_view(), name='update_service'),
    path('remove/<int:service_id>', RemoveService.as_view(), name='remove_service'),
]