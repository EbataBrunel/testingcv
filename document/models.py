from django.db import models
from django.contrib.auth.models import User
from forum.models import*

class Cours(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    discipline=models.ForeignKey(Discipline, on_delete=models.CASCADE, null=False)
    composant=models.ForeignKey(Composant, on_delete=models.CASCADE, null=False)
    file=models.FileField(upload_to="upload", null=False)
    title=models.CharField(max_length=100, null=True)
    LEVEL=[
        ('Baccalauréat','Baccalauréat'),
        ('Bac + 1','Bac + 1'),
        ('Bac + 2','Bac + 2'),
        ('Bac + 3','Bac + 3'),
        ('Bac + 4','Bac + 4'),
        ('Bac + 5','Bac + 5'),
        ('Bac + 6','Bac + 6'),
        ('Bac + 7','Bac + 7'),
    ]
    niveau=models.CharField(max_length=200, null=True, choices=LEVEL)
    comment=models.CharField(max_length=500, null=True)
    TP=[
        ('Gratuit','Gratuit'),
        ('Payant','Payant')
    ]
    type=models.CharField(max_length=100, null=True, choices=TP)
    price=models.IntegerField(default=0, null=True)
    date=models.DateField(auto_created=True)
    ST=[
        ('Traitement en cours','Traitement en cours'),
        ('Cours publié','Cours publié'),
        ('Cours non retenu','Cours non retenu')
    ]
    status=models.CharField(max_length=100, null=True, choices=ST, default="Traitement en cours")
    st=models.IntegerField(default=0,null=True)
    content=models.TextField(null=True)

class Panier(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    cquantite=models.TextField(max_length=100, null=True)

class Commande(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ucours=models.TextField(max_length=500,null=True)
    total=models.IntegerField(null=False)
    datecommande=models.DateField(auto_now=True)
    status=models.BooleanField(default=False)
    statusachat=models.BooleanField(default=False)
