from django.db import models
from users.models import User
from service.models import Service
# Create your models here.

class Preferences(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    picture = models.ImageField(upload_to='preferences_pictures/', blank=True, null=True)
    users = models.ManyToManyField(User, related_name='preferences')
    services = models.ManyToManyField(Service, related_name='preferences')
