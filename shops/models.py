from django.db import models

from common.models import BaseModel


# Create your models here.

def default_translated_languages():
    return ["en"]


class Shop(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    cover_image = models.JSONField(default=dict, blank=True, null=True)
    logo = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    settings = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name
