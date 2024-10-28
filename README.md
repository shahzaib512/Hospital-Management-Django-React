erDiagram
    User ||--o{ Patient : is
    User ||--o{ Doctor : is
    User ||--o{ Admin : is
    Patient ||--o{ Appointment : books
    Doctor ||--o{ Appointment : handles
    Patient ||--o{ MedicalRecord : has
    Doctor ||--o{ MedicalRecord : creates
    Appointment ||--o{ Prescription : has
    MedicalRecord ||--o{ Prescription : contains
    Department ||--o{ Doctor : belongs_to

    User {
        int id PK
        string email
        string password
        string full_name
        string phone
        enum role
        datetime created_at
        boolean is_active
    }

    Patient {
        int id PK
        int user_id FK
        string blood_group
        date date_of_birth
        string address
        string emergency_contact
    }

    Doctor {
        int id PK
        int user_id FK
        int department_id FK
        string specialization
        text qualifications
        boolean is_available
    }

    Admin {
        int id PK
        int user_id FK
        string designation
    }

    Appointment {
        int id PK
        int patient_id FK
        int doctor_id FK
        datetime appointment_time
        string status
        text reason
        boolean is_confirmed
    }

    MedicalRecord {
        int id PK
        int patient_id FK
        int doctor_id FK
        date visit_date
        text diagnosis
        text treatment_plan
        text notes
    }

    Prescription {
        int id PK
        int appointment_id FK
        int medical_record_id FK
        string medicine_name
        string dosage
        text instructions
        date prescribed_date
    }

    Department {
        int id PK
        string name
        string description
    }
