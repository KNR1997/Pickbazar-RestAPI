from django.db import models

from common.models import BaseModel


def default_translated_languages():
    return ["en"]

# Create your models here.
class FAQ(BaseModel):
    faq_title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    faq_description = models.TextField()
    faq_type = models.CharField(max_length=55, default='global', blank=True, null=True)
    issued_by = models.CharField(max_length=25, default='Super Admin', blank=True, null=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)

    def __str__(self):
        return self.faq_title


class TermsAndConditions(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    type = models.CharField(max_length=55, default='global', blank=True, null=True)
    issued_by = models.CharField(max_length=25, default='Super Admin', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)

    def __str__(self):
        return self.title