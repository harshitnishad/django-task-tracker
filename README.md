Django Task Tracker

A simple backend task tracking system built using Django.
The project supports user authentication, project management, and task management with REST-style APIs.
All APIs were tested using Postman.

Features

User login & logout

Create and list projects

Create, list, update, and delete tasks

Tasks belong to projects

Authentication required for all APIs

Permissions: users can only access their own data

Tech Stack

Python 3

Django 6.0

SQLite (default Django database)

Project Setup
1️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

2️⃣ Install dependencies
pip install django

3️⃣ Run migrations
python manage.py migrate

4️⃣ Create superuser (optional)
python manage.py createsuperuser

5️⃣ Start the server
python manage.py runserver


Server will run at:

http://127.0.0.1:8000/

Authentication
Action	URL
Login	/login/
Logout	/logout/

After login, user is redirected to /projects/

Authentication is required for all APIs

API Endpoints
📁 Projects API
Method	Endpoint	Description
GET	/projects/	List user projects
POST	/projects/	Create a project

POST /projects/

{
  "name": "My Project",
  "description": "Project description"
}

📝 Tasks API
Method	Endpoint	Description
GET	/tasks/	List tasks
POST	/tasks/	Create task
PUT	/tasks/<id>/	Update task
DELETE	/tasks/<id>/	Delete task

POST /tasks/

{
  "title": "Task title",
  "project_id": 1,
  "description": "Task details",
  "priority": 3,
  "status": "todo"
}

Testing

All APIs tested using Postman

Supported operations:

Create Project

Create Task

List Tasks

Update Task

Delete Task

Admin Panel

Admin panel available at:

/admin/


Models registered:

Project

Task

Notes

/ root URL returns 404 (no homepage implemented)

This is expected behavior

Designed as a backend-focused assignment

Author

Harshit Nishad