from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('policyholder', 'Policyholder'),
    )

    role    = models.CharField(max_length=20, choices=ROLE_CHOICES, default='policyholder')
    phone   = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # ── Convenience helpers ──────────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_policyholder(self):
        return self.role == 'policyholder'

    @property
    def dashboard_url(self):
        """Return the correct dashboard URL name for this user's role."""
        mapping = {
            'admin':        'admin_dashboard',
            'staff':        'staff_dashboard',
            'policyholder': 'policyholder_dashboard',
        }
        return mapping.get(self.role, 'policyholder_dashboard')

# Create your models here.
