"""persianoscar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.views.generic import RedirectView
from oscar.app import application as oscar
from oscar.app import application
# t
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from oscarapi.app import application as api

from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    # url(r'', oscar.urls),
    path('oscarapi/', api.urls),
    # url(r'^$', RedirectView.as_view(url='/catalogue/')),
    url(r'', application.urls),
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    url(r'^payment/', include('pay_ir.urls'))

    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.

    # url(r'', include(application.urls))
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
