from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import PolicyHolder

User = get_user_model()


@receiver(post_save, sender=User)
def create_policyholder(sender, instance, created, **kwargs):

    if created:

        PolicyHolder.objects.create(
            user=instance
        )