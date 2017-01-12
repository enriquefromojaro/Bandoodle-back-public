"""BandoodleBackEnd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import View
from rest_framework.routers import DefaultRouter

from BandoodleBackEnd import settings
from bands.views import BandViewSet
from timeOptions.views import TimeOptionViewSet
from users.views import MusicianViewSet, login
from events.views import EventViewSet
from users.routers import pwd_routes

api_prefix = 'api/'
router = DefaultRouter()
router.register(r'users', MusicianViewSet)
router.register(r'bands', BandViewSet)
router.register(r'timeoptions',TimeOptionViewSet)
router.register(r'events',EventViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^'+api_prefix, include(router.urls)),
    url(r'', include(pwd_routes)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login/$', login),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
