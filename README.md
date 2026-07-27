# HR Mehndi - Django Project

Authentic Bridal Henna & Handcrafted Arts booking website built with pure Django + Tailwind CSS.

---

## 🚀 Quick Setup (5 Steps)

### Step 1 — Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2 — Install Requirements
```bash
pip install -r requirements.txt
```

### Step 3 — Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4 — Create Admin User
```bash
python manage.py createsuperuser
```
Enter your desired username, email, and password when prompted.

### Step 5 — Start the Server
```bash
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000/**

Admin panel: **http://127.0.0.1:8000/admin/**

---

## 📁 Project Structure

```
hrmehndi_project/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← created after migrate
├── hrmehndi_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── bookings/
│   ├── models.py           ← BookingInquiry, MehndiDesign, DesignImage
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── static/
│   └── css/style.css
├── templates/
│   └── home.html
└── media/                  ← uploaded images go here
    ├── covers/
    └── gallery/
```

---

## 🎨 How to Add Designs via Admin

1. Go to **http://127.0.0.1:8000/admin/**
2. Log in with your superuser account
3. Click **Mehndi Designs → Add**
4. Fill in title, upload a **Cover Image**, add description
5. Use the **Design Images** inline section to add extra photos (palm, back, feet views)
6. Click **Save**

The design will appear on the homepage gallery automatically!

---

## 📋 Managing Bookings

All booking form submissions appear in the admin under **Booking Inquiries**.

You can:
- View all client details, dates, locations
- Change **Status** (Pending → Confirmed → Completed) directly from the list view
- Search and filter by date, service type, or status

---

## 🔧 Notes

- `DEBUG = True` is set for development. Change to `False` for production.
- Update `SECRET_KEY` in `settings.py` before going live.
- `ALLOWED_HOSTS = ['*']` is open for local dev — restrict it in production.
- Media files (uploaded images) are stored in the `/media/` folder.
