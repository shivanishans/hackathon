from django.db import models

# Create your models here.
class Message(models.Model):
    sender_id = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    text = models.TextField()
    is_abusive = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender}: {self.text}'
