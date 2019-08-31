from django.db import models
from oscar.core.compat import AUTH_USER_MODEL
from oscar.core.loading import get_class


# Create your models here.
class Abstractdigital(models.Model):
    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        related_name='digitalassest',
        on_delete=models.CASCADE,
        verbose_name="Owner")
    video_url = models.URLField()
