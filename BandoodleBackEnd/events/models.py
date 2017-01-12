from django.db import models

# Create your models here.
from bands.models import Band


class Event (models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    address = models.CharField(null=False, blank=False, max_length=100)
    type = models.CharField(null=False, blank=False, max_length=20, choices=[('gig','gig'),('rehearsal','rehearsal')])
    band = models.ForeignKey(Band, related_name='events')
    description = models.CharField(max_length=200, null=False, blank=True, default='Descripción pendiente')

    def __str__(self):
        return self.name
