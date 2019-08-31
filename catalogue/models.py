from django.db import models

# Create your models here.
# from django.urls import reverse
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    video_url = models.URLField()

    # class Meta:
    #     permissions = (('assign_sold', 'Assign sold'),)


from oscar.apps.catalogue.models import *

# #
