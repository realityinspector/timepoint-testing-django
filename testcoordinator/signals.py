from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Count


@receiver(post_save, sender=User)
def make_first_user_admin(sender, instance, created, **kwargs):
    """
    Signal to automatically make the first user in the system a superuser/admin.
    This ensures that the first person who signs up gets full admin access.
    """
    if created:  # Only run this for newly created users
        # Count all users in the system
        user_count = User.objects.count()
        
        # If this is the first user (or if there's only one user in the system)
        if user_count == 1:
            # Make this user a superuser and staff member
            instance.is_superuser = True
            instance.is_staff = True
            
            # Save the user without triggering this signal again
            # This avoids an infinite loop
            post_save.disconnect(make_first_user_admin, sender=User)
            instance.save()
            post_save.connect(make_first_user_admin, sender=User) 