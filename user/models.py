from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    password   = models.CharField(max_length=255)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # --- Below: not DB fields, just properties Django's auth machinery
    # (IsAuthenticated, JWTAuthentication) checks on request.user.
    # No migration needed for these — they don't touch the schema.

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False