from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, AppointmentViewSet, upload_excel

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/upload/', upload_excel, name='upload-excel'),  # Upload endpoint under /api/upload/  
]
