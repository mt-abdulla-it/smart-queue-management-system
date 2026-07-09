# 🏥 Smart Queue Management System

### For Hospitals and Government Offices in Sri Lanka

A production-ready, full-stack web application that digitizes queue management with real-time tracking, online booking, QR tokens, and live dashboards.

**Final Year Project** | University of Sri Lanka

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13+, Django 5+, Django REST Framework |
| **Database** | PostgreSQL |
| **Real-time** | Django Channels, WebSockets, Redis |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript, AJAX |
| **Auth** | JWT (SimpleJWT), Role-Based Access Control |
| **Reports** | ReportLab (PDF), openpyxl (Excel), Chart.js |
| **Other** | QR Code generation, Email notifications |

## 📋 Features

### User Features
- ✅ Register, Login, Forgot Password, Edit Profile
- ✅ Book Queue Online / View Current Position
- ✅ Real-time Wait Time Tracking
- ✅ QR Code Token / PDF Download
- ✅ Email & SMS Notifications
- ✅ Submit Feedback / View Queue History

### Staff Features
- ✅ Call Next / Skip / Hold / Complete Token
- ✅ Search Queue / View Today's Queue
- ✅ Real-time Queue Statistics

### Admin Features
- ✅ Manage Users, Staff, Branches, Services
- ✅ Dashboard with Analytics Charts
- ✅ Generate Reports (PDF / Excel)
- ✅ Feedback Management / System Settings

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.13+
- PostgreSQL 14+
- Redis 7+
- Git

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/smart-queue-management-system.git
cd smart-queue-management-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your database credentials

# 5. Create PostgreSQL database
# psql -U postgres
# CREATE DATABASE smart_queue_db;

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Run development server
python manage.py runserver
```

### Access the Application
- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

---

## 📁 Project Structure

```
smart-queue-management-system/
├── config/                     # Project configuration
│   └── settings/               # Split settings (base/dev/prod)
├── apps/
│   ├── accounts/               # User authentication & profiles
│   ├── branches/               # Branches, departments, services
│   ├── queues/                 # Queue token management
│   ├── notifications/          # Email/SMS notifications
│   ├── feedback/               # User feedback
│   ├── reports/                # PDF/Excel reports
│   ├── dashboard/              # Admin & staff dashboards
│   ├── api/                    # REST API (versioned)
│   └── core/                   # Shared utilities
├── templates/                  # Global templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User uploads
└── docs/                       # Documentation
```

---

## 📄 License

This project is developed as a university final-year project.

---

## 👤 Author

**Your Name**
- University: [Your University]
- Supervisor: [Your Supervisor]

---

*Solving real-world queue problems in Sri Lanka 🇱🇰*
