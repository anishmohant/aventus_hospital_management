from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
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

        # Validate required columns
        required_patient_columns = {'Patient ID', 'Patient Name', 'Contact Information', 'Date of Birth', 'Gender'}
        required_appointment_columns = {'Appointment ID', 'Patient ID', 'Doctor Name', 'Department', 'Appointment Date', 'Appointment Time', 'Reason for Visit'}
        
        if not required_patient_columns.issubset(df_patients.columns) or not required_appointment_columns.issubset(df_appointments.columns):
            return Response({"error": "Missing required columns in Excel sheets"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert dataframes to dictionaries for faster processing
        patients_data = df_patients.to_dict('records')
        appointments_data = df_appointments.to_dict('records')

        # Get existing patients to avoid duplicate lookups
        existing_patients = Patient.objects.in_bulk(field_name='patient_id')
        new_patients = []
        updated_patients = []

        # Iterate over patient data
        for row in patients_data:
            patient_id = row['Patient ID']
            patient_data = {
                'patient_id': patient_id,
                'name': row['Patient Name'],
                'contact_info': row['Contact Information'],
                'medical_history': row.get('Medical History', ''),
                'date_of_birth': remove_alphabets_and_commas(row['Date of Birth']),
                'gender': row['Gender']
            }

            if patient_id in existing_patients:
                # Update existing patient
                patient = existing_patients[patient_id]
                for field, value in patient_data.items():
                    setattr(patient, field, value)
                updated_patients.append(patient)
            else:
                # Create new patient
                new_patients.append(Patient(**patient_data))

        # Bulk create new patients and update existing ones
        if new_patients:
            Patient.objects.bulk_create(new_patients)
        if updated_patients:
            Patient.objects.bulk_update(updated_patients, ['name', 'contact_info', 'medical_history', 'date_of_birth', 'gender'])

        # Get updated patient list for fast lookups during appointments processing
        updated_patients_lookup = {p.patient_id: p for p in Patient.objects.all()}
        new_appointments = []
        updated_appointments = []

        # Iterate over appointment data
        for row in appointments_data:
            patient_id = row['Patient ID']
            if patient_id not in updated_patients_lookup:
                return Response({"error": f"Patient ID {patient_id} not found"}, status=status.HTTP_400_BAD_REQUEST)

            patient = updated_patients_lookup[patient_id]
            appointment_id = row['Appointment ID']
            appointment_data = {
                'appointment_id': appointment_id,
                'patient': patient,
                'doctor_name': row['Doctor Name'],
                'department': row['Department'],
                'appointment_date': remove_alphabets_and_commas(row['Appointment Date']),
                'appointment_time': remove_alphabets_and_commas(row['Appointment Time']),
                'reason_for_visit': row['Reason for Visit'],
            }

            existing_appointment = Appointment.objects.filter(appointment_id=appointment_id).first()
            if existing_appointment:
                # Update existing appointment
                for field, value in appointment_data.items():
                    setattr(existing_appointment, field, value)
                updated_appointments.append(existing_appointment)
            else:
                # Create new appointment
                new_appointments.append(Appointment(**appointment_data))

        # Bulk create new appointments and update existing ones
        if new_appointments:
            Appointment.objects.bulk_create(new_appointments)
        if updated_appointments:
            Appointment.objects.bulk_update(updated_appointments, ['patient', 'doctor_name', 'department', 'appointment_date', 'appointment_time', 'reason_for_visit'])

        return Response({"success": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


