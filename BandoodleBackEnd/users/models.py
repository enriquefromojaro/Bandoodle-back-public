from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/users/user_<id>/<filename>
    return 'images/users/user_{0}/{1}'.format(instance.user.id, filename)


# Create your models here.
class Musician(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to=user_directory_path, null=False, blank=False)
