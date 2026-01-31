from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Crop(models.Model):
    SEASON_CHOICES = [
        ('Rabi', 'Rabi'),
        ('Kharif', 'Kharif'),
        ('Zaid', 'Zaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    area = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.state}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update UserProfile when User is saved
    """
    if created:
        UserProfile.objects.create(user=instance, state='Delhi', city='Delhi')
    else:
        # Ensure profile exists for existing users
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance, state='Delhi', city='Delhi')