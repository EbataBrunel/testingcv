from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

# Create your models here.
class Annonce(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title=models.CharField(max_length=100)
    content=RichTextField(blank=True, null=False)
    company=models.CharField(max_length=100, null=True)
    date=models.DateTimeField(auto_now_add=True)

