from django.contrib import admin

# Register your models here.
from users.models import Musician

admin.site.register(Musician)
