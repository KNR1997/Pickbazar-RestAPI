from django.db import models

from common.models import BaseModel


# Create your models here.

class Settings(BaseModel):
    language = models.CharField(max_length=10, default='en')
    options = models.JSONField()  # Store all settings-related data

    def __str__(self):
        return f"Settings ({self.language})"
