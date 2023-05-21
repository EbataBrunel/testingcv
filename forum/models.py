from django.db import models
from ckeditor.fields import RichTextField
from eab.models import*

class Discipline(models.Model):
    libelle=models.CharField(max_length=200)

    def __str__(self):
        return self.libelle

class Composant(models.Model):
    discipline=models.ForeignKey(Discipline, on_delete=models.CASCADE, null=True)
    libelle=models.CharField(max_length=200)

    def __str__(self):
        return self.libelle
    
class Question(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    discipline=models.ForeignKey(Discipline, on_delete=models.CASCADE, null=True)
    composant=models.ForeignKey(Composant, on_delete=models.CASCADE, null=False)  
    subject=models.CharField(max_length=200, null=False)
    content=RichTextField(blank=True, null=False)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class Answer(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    question=models.ForeignKey(Question, on_delete=models.CASCADE, null=False)
    content=RichTextField(blank=True, null=False)
    date=models.DateTimeField(auto_now_add=True)
    status=models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.content
    
class Likes(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    question=models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user
    
class Likeanswer(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    answer=models.ForeignKey(Answer, on_delete=models.CASCADE, null=False)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user