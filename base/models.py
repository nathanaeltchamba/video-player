import subprocess
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from datetime import timedelta
from django.conf import settings

# Create your models here.
class CustomProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=50, null=True)
    bio = models.TextField(blank=True, default='', null=True)

class VideoModel(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    video_upload = models.FileField(null=True, upload_to='uploads/videos', validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])])
    thumbnail_upload = models.FileField(null=True, upload_to='uploads/thumbnails', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    view_count = models.IntegerField(default=0)
    # duration = models.CharField(max_length=20, default='N/A')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    is_private = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.video_upload.delete()
        self.thumbnail_upload.delete()
        super().delete(*args, **kwargs)

    def elapsed_time(self):
        now = timezone.now()
        elapsed_time = now - self.uploaded_at
        if elapsed_time <= timedelta(minutes=1):
            return 'just now'
        elif elapsed_time <= timedelta(hours=1):
            return f'{elapsed_time.seconds // 60} mins ago'
        elif elapsed_time <= timedelta(days=1):
            return f'{elapsed_time.seconds // 3600} hours ago'
        elif elapsed_time <= timedelta(weeks=2):
            return f'{elapsed_time.days} days ago'
        elif elapsed_time <= timedelta(days=30):
            return f'{elapsed_time.days // 7} weeks ago'
        elif elapsed_time <= timedelta(days=365):
            return f'{elapsed_time.days // 30} months ago'
        else:
            return f'{elapsed_time.days // 365} years ago'



def pre_save_video_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

pre_save.connect(pre_save_video_receiver, sender=VideoModel)


class CronJobLock(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)
    locked_at = models.DateTimeField(auto_now_add=True)

class CronJobLog(models.Model):
    job = models.CharField(max_length=100)
    run_at = models.DateTimeField(auto_now_add=True)


class Test(models.Model):
    name = models.CharField(max_length=4)