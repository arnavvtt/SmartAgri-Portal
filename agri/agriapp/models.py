from django.db import models
from django.db import models
from django.contrib.auth.models import User

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

# Create your models here.
