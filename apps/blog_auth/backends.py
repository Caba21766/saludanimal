from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class DNIBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        try:
            user = User.objects.get(dni_usuario=username)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Evita traceback si aún quedan DNIs duplicados: no autentica
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
