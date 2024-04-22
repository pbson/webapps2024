from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class RegisterConfig(AppConfig):
    name = 'register'

    def ready(self):
        User = get_user_model()
        try:
            User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1')
        except IntegrityError:
            pass
