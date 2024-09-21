from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    is_merged = models.BooleanField(default=False)
    is_trimmed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
