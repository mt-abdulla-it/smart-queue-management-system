<div align="center">
  <h1>🏥 Smart Queue Management System (SQMS)</h1>
  <p><strong>A production-ready, full-stack web application that digitizes queue management with real-time tracking, online booking, QR tokens, and live dashboards.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Django-5+-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/PostgreSQL-14+-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Redis-7+-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
    <img src="https://img.shields.io/badge/Bootstrap-5-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
  </p>

  <p><em>Built specifically for Hospitals and Government Offices in Sri Lanka 🇱🇰</em></p>
</div>

<br />

## 🎥 Cinematic Product Demo
Check out the fully automated, 60FPS cinematic showcase of the Smart Queue Management System in action! It demonstrates the entire end-to-end flow from patient booking to staff queue management.

> 📥 **[Download & Watch the Cinematic Demo Video (MP4) Here](./SQMS_Cinematic_Demo_Final.mp4)**

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
| **Other** | QR Code generation, Email & WebSocket notifications |

---

## 📋 Features

### 👤 User (Patient/Client) Features
- ✅ **Secure Access:** Register, Login, Forgot Password, Edit Profile
- ✅ **Online Booking:** Book Queue Online & View Current Position
- ✅ **Live Tracking:** Real-time Wait Time Tracking via WebSockets
- ✅ **Digital Tokens:** QR Code Token Generation & PDF Download
- ✅ **Notifications:** Automated Email & WebSocket alerts
- ✅ **History:** Submit Feedback & View Queue History

### 👨‍💼 Staff Features
- ✅ **Queue Control:** Call Next, Skip, Hold, or Complete Tokens
- ✅ **Dashboard:** Real-time Staff Dashboard & Queue Processing
- ✅ **Management:** Search Queue & View Today's Queue roster
- ✅ **Analytics:** Live Queue Statistics

### 🛡️ Admin Features
- ✅ **System Control:** Manage Users, Staff, Branches, and Services
- ✅ **Analytics:** Advanced Dashboard with Chart.js visual analytics
- ✅ **Exporting:** Generate detailed Reports (PDF / Excel)
- ✅ **Settings:** Feedback Management & System Settings

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python** 3.13+
- **PostgreSQL** 14+
- **Redis** 7+ (Required for WebSockets)
- **Git**

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/mt-abdulla-it/smart-queue-management-system.git
cd smart-queue-management-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database and Redis credentials

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

# 9. Run development server (ASGI server for WebSockets)
python manage.py runserver
```

### Access the Application
- **Homepage**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin/`
- **API Docs**: `http://localhost:8000/api/docs/`

---

## 📁 Project Structure

```text
smart-queue-management-system/
├── config/                     # Project configuration & settings (base/dev/prod)
├── apps/                       # Django applications
│   ├── accounts/               # User authentication & profiles
│   ├── branches/               # Branches, departments, services
│   ├── queues/                 # Queue token management & real-time tracking
│   ├── notifications/          # Email/SMS & WebSocket notifications
│   ├── feedback/               # User feedback
│   ├── reports/                # PDF/Excel reports
│   ├── dashboard/              # Admin & staff dashboards
│   ├── api/                    # REST API (versioned)
│   └── core/                   # Shared utilities
├── templates/                  # Global HTML templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User uploads
└── docs/                       # Documentation
```

---

## 👤 Author

**Abdulla Thaslim**  
[![GitHub](https://img.shields.io/badge/GitHub-mt--abdulla--it-181717?style=flat-square&logo=github)](https://github.com/mt-abdulla-it)
[![Email](https://img.shields.io/badge/Email-mt.abdulla.it%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:mt.abdulla.it@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mt--abdulla--it-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/mt-abdulla-it/)

---
*Solving real-world queue problems in Sri Lanka 🇱🇰*
