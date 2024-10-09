from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient, Appointment
from .serializers import PatientSerializer, AppointmentSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import pandas as pd
import re

# ViewSet for managing Patient records
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'medical_history', 'date_of_birth', 'gender']
    search_fields = ['name']

# ViewSet for managing Appointment records
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['patient__patient_id', 'doctor_name', 'department', 'appointment_date']
    search_fields = ['patient__name']

# Cleaning Uploaded Data
def remove_alphabets_and_commas(text):
  text = re.sub(r'[a-zA-Z]', '', text)
  text = text.replace(',', '')
  text = text.replace(' ', '')
  return text

# API view for bulk upload of data from Excel
@api_view(['POST'])
def upload_excel(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
    
    excel_file = request.FILES['file']
    try:
        # Parse the Excel file for Patients and Appointments
        df_patients = pd.read_excel(excel_file, sheet_name='Patients')
        df_appointments = pd.read_excel(excel_file, sheet_name='Appointments')

        # Validate and save patient data
        for _, row in df_patients.iterrows():
            if not all([row.get('Patient ID'), row.get('Patient Name'), row.get('Contact Information'),
                        row.get('Date of Birth'), row.get('Gender')]):
                return Response({"error": "Missing required patient information"}, status=status.HTTP_400_BAD_REQUEST)

            Patient.objects.update_or_create(
                patient_id=row['Patient ID'],
                defaults={
                    'name': row['Patient Name'],
                    'contact_info': row['Contact Information'],
                    'medical_history': row.get('Medical History', ''),
                    'date_of_birth': remove_alphabets_and_commas(row['Date of Birth']),
                    'gender': row['Gender']
                }
            )

        # Validate and save appointment data
        for _, row in df_appointments.iterrows():
            try:
                patient = Patient.objects.get(patient_id=row['Patient ID'])
                Appointment.objects.update_or_create(
                    appointment_id=row['Appointment ID'],
                    defaults={
                        'patient': patient,
                        'doctor_name': row['Doctor Name'],
                        'department': row['Department'],
                        'appointment_date': remove_alphabets_and_commas(row['Appointment Date']),
                        'appointment_time': remove_alphabets_and_commas(row['Appointment Time']),
                        'reason_for_visit': row['Reason for Visit']
                    }
                )
            except Patient.DoesNotExist:
                return Response({"error": f"Patient ID {row['Patient ID']} not found"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


