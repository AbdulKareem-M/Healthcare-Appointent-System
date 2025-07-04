# Healthcare Appointment System

A web-based application designed to streamline hospital administration by managing patient appointments, doctor schedules, and related healthcare workflows.

## Features

- Patient registration and profile management
- Doctor scheduling and availability
- Appointment booking and cancellation
- Admin dashboard for managing users and appointments
- Email/SMS notifications for reminders

## Technologies Used

- Framework: Django (Python)
- Database: SQLite (default, configurable)
- Authentication: Django's built-in authentication system

## Getting Started

1. **Clone the repository:**
  ```bash
  git clone https://github.com/yourusername/Healthcare_Appointment_System.git
  cd Healthcare_Appointment_System
  ```

2. **Create and activate a virtual environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

3. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

4. **Apply migrations:**
  ```bash
  python manage.py migrate
  ```

5. **Run the development server:**
  ```bash
  python manage.py runserver
  ```

## Folder Structure

```
/Healthcare_Appointment_System
  ├── appointments/   # Main Django app
  ├── doctor_profiles/   # Main Django app
  ├── Healthcare_Appointment_System/  # Project settings
  ├── manage.py
  ├── requirements.txt
  └── README.md
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.