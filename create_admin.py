import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = 'admin@example.com'
password = 'admin123'

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, first_name='Admin', last_name='System')
    print(f"✅ Success! Admin user created.")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
else:
    print(f"⚠️ User with email {email} already exists.")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
