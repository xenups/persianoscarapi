from django.shortcuts import render
from django.views.generic import DetailView, ListView

# Create your views here.
from digital.models import Abstractdigital


class DigitalAssesst(ListView):
    queryset = Abstractdigital.objects.all()
    print(queryset.all())
