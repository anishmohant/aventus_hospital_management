# Aventus Hospital Management System




Hospital Management Created wit Django Rest Framework


- Django Rest Framework
- SQlite3


## Features

- Bulk Upload Patients and their Appointments
- CRUD Operations on Patient And Appointments.
- Filteriing on records of Patients



## Installation

This Project need Python to RUN

```sh
clone project
create venv and install requirements.txt
cd aventus_hospital_management
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
You will see Output as follows.
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```


## Usage

You can Access the software via API calls.
We assume the software is running at http://127.0.0.1:8000/


#### Bulk Upload
You can bulk upload your excel files by making a 
```
POST : http://127.0.0.1:8000/upload/
```
with one form and only one file upload


#### Create Patient
You can create patient one by one
```
POST http://127.0.0.1:8000/api/patients/
```
with JSON body for example
```
{
  "patient_id": "P081766",
  "name": "Anish Mohan",
  "contact_info": "+1-553-730-4881, nish96@example.org",
  "medical_history": "Asthma",
  "date_of_birth": "1968-09-15",
  "gender": "Male"
}
```

Similiarly to edit a record of Patient,
```
PUT http://127.0.0.1:8000/api/patients/P0817/
```
with JSON body
```
{
  "patient_id": "P081766",
  "name": "Anish Mohan K",
  "contact_info": "+1-553-730-4881, anish@example.org",
  "medical_history": "Asthma",
  "date_of_birth": "1968-09-15",
  "gender": "Male"
}
```

___________________
#### Read Appointment
```
GET http://127.0.0.1:8000/api/appointments/A0002
```
Output
```
{
  "appointment_id": "A0002",
  "doctor_name": "Dr. Bob White",
  "department": "Orthopedics",
  "appointment_date": "2025-04-09",
  "appointment_time": "09:30:00",
  "reason_for_visit": "Annual physical exam",
  "patient": "P0705"
}
```

#### Read appointments of a particular patient
```
GET http://127.0.0.1:8000/api/appointments/?patient__patient_id=P0179
```
Output
```
[
  {
    "appointment_id": "A0237",
    "doctor_name": "Dr. Cathy Blue",
    "department": "Neurology",
    "appointment_date": "2025-04-02",
    "appointment_time": "11:00:00",
    "reason_for_visit": "Consultation",
    "patient": "P0179"
  },
  {
    "appointment_id": "A0393",
    "doctor_name": "Dr. Cathy Blue",
    "department": "Cardiology",
    "appointment_date": "2024-07-09",
    "appointment_time": "13:00:00",
    "reason_for_visit": "Annual physical exam",
    "patient": "P0179"
  }
]
```

ALL the CURD Operations are implemented in the project.

