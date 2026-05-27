import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canacintra_project.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.views import admin_noticias

user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()

factory = RequestFactory()
request = factory.get('/dashboard/noticias/')
request.user = user

try:
    response = admin_noticias(request)
    print("STATUS:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
