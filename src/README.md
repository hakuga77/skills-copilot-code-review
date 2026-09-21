# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements/active`                                           | Get currently active announcements for the public homepage banner   |
| GET    | `/announcements?teacher_username=...`                              | Get all announcements, including expired ones (requires auth)       |
| POST   | `/announcements?message=...&expiration_date=YYYY-MM-DD&teacher_username=...&start_date=YYYY-MM-DD` | Create an announcement (requires auth, `start_date` optional) |
| PUT    | `/announcements/{announcement_id}?message=...&expiration_date=YYYY-MM-DD&teacher_username=...&start_date=YYYY-MM-DD` | Update an announcement (requires auth) |
| DELETE | `/announcements/{announcement_id}?teacher_username=...`            | Delete an announcement (requires auth)                              |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
