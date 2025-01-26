from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

@receiver(pre_delete, sender=User)
def clear_username_on_delete(sender, instance, **kwargs):
    # Clear the username when a user is deleted
    instance.username = f"deleted_{instance.username}_{instance.id}"
    instance.save()
