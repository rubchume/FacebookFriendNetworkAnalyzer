from django.db import models


class ScanInstance(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=255)
    file = models.FileField(upload_to="networks")


class LogEvent(models.Model):
    scan_instance = models.ForeignKey(ScanInstance, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
