from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from events.models import Event


class TimeOption (models.Model):
    date = models.DateField(null=False, blank=False, validators=[
        MinValueValidator(datetime.today().date())
    ])
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=True)
    voted_by = models.ManyToManyField(User, blank=False, related_name='voted_time_options')
    event = models.ForeignKey(Event, related_name='time_options')


    def __str__(self):
        return str(self.date)+' ( '+str(self.start_time) + ' - '+ str(self.end_time) + ')'