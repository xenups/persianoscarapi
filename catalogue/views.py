from django.shortcuts import render

# Create your views here.
from oscar.apps.promotions.views import HomeView as CoreHomeView

class HomeView(CoreHomeView):
    template_name = 'new-homeview.html'
