from django.db import models
from django.contrib.auth.models import User


# Create your models here.
def band_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/bands/band_<id>/<filename>
    return 'images/bands/band_{0}/{1}'.format(instance.pk, filename)

class Band(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    genre = models.CharField(max_length=50, null=True, blank=True,
                             choices=[('Rock', 'Rock'), ('Rock & Roll', 'Rock & Roll'), ('Metal', 'Metal'),
                                      ('Heavy Metal', 'Heavy Metal'), ('Deathtukada', 'Deathtukada')])
    users = models.ManyToManyField(User, related_name='bands', blank=False)
    invited_users = models.ManyToManyField(User,  related_name='requested_bands', blank=True)
    avatar = models.ImageField(upload_to=band_directory_path, null=False, blank=False)

    def __str__(self):
        return self.name
