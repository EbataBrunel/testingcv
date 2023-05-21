from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    phone=models.CharField(max_length=100)
    address=models.TextField()
    photo=models.ImageField(upload_to="media", null=True, blank=True)
    SEX=[
        ('Masculin','Masculin'),
        ('Feminin','Feminin')
    ]
    gender=models.CharField(max_length=100, null=True, choices=SEX)
    droitmes=models.BooleanField(default=False, null=True)
    status=models.BooleanField(default=False, null=True)
    apropos=models.TextField(null=True)
    profession=models.CharField(max_length=50, null=True)
    VARIABLE=[
        ('Visible','Visible'),
        ('Invisible','Invisible')
    ]
    vform=models.CharField(max_length=100, null=True, choices=VARIABLE, default="Visible")
    vep=models.CharField(max_length=100, null=True, choices=VARIABLE)
    vcomp=models.CharField(max_length=100, null=True, choices=VARIABLE)
    vaform=models.CharField(max_length=100, null=True, choices=VARIABLE)
    priority=models.BooleanField(null=True,default=False)

    def __str__(self):
        return str(self.user)
    
class Annee(models.Model):
    libelle=models.CharField(max_length=4, unique=True, null=True)

    def __str__(self):
        return self.libelle
    
class Parametre(models.Model):
    appname=models.CharField(max_length=100)
    appeditor=models.CharField(max_length=200)
    phone=models.CharField(max_length=200, null=True)
    email=models.CharField(max_length=200, null=True)
    version=models.CharField(max_length=10, null=True)
    devise=models.CharField(max_length=10, null=True)
    COLORS=[
        ('primary','primary'),
        ('info','info'),
        ('success','success'),
        ('danger','danger'),
        ('secondary','secondary'),
        ('dark','dark'),
    ]
    theme=models.CharField(max_length=200, null=True, choices=COLORS)
    logo=models.ImageField(upload_to="media", null=True, blank=True)
    width_logo=models.CharField(max_length=3, null=True)
    height_logo=models.TextField(max_length=3, null=True)

    def __str__(self):
        return self.appname
    
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    subject=models.TextField()
    message=models.TextField(null=True)
    datecontact=models.DateTimeField(null=True, blank=True, auto_now_add=True)
    statut=models.IntegerField(null=True)
    codes=models.CharField(max_length=300, null=True)
    status=models.IntegerField(null=True)
    statutdel=models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.name

class Etablissement(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name=models.CharField(max_length=200)
    country=models.CharField(max_length=100)
    city=models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Formation(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    intitule=models.CharField(max_length=200)

    def __str__(self):
        return self.intitule


class Entreprise(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    city=models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Parcours(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    annee=models.ForeignKey(Annee, on_delete=models.CASCADE, null=True)
    annee1=models.IntegerField(default=0, null=True)
    etablissement=models.ForeignKey(Etablissement, on_delete=models.CASCADE, null=True)
    formation=models.ForeignKey(Formation, on_delete=models.CASCADE, null=True)
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
    status=models.BooleanField(null=True)
    statusan=models.CharField(max_length=50, null=True, default="Non")

class Competence(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    TYPE=[
        ('Langue','Langue'),
        ('Bureautique','Bureautique'),
        ("Système d'exploitation","Système d'exploitation"),
        ('Logiciel','Logiciel'),
        ('Technologie web','Technologie web'),
        ('Langage de programmation','Langage de programmation'),
        ('Framework','Framework'),
        ('Système de Gestion de Base de Données', 'Système de Gestion de Base de Données'),
        ('Outil et Environnement','Outil et Environnement'),
        ('Modélisation','Modélisation'),
        ('Loisir','Loisir')
    ]
    type_comp=models.CharField(max_length=100, null=False, choices=TYPE)
    name=models.CharField(max_length=100, null=True)
    comment=models.TextField(null=True)
    status=models.BooleanField(null=True)

    def __str__(self):
        return self.type_comp


class Experience(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    TYPE=[
        ('Employé(e)','Employé(e)'),
        ('Stagiaire','Stagiaire'),
    ]
    type_exp=models.CharField(max_length=100, null=False, choices=TYPE)
    entreprise=models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=False)
    posteoccupe=models.CharField(max_length=200)
    PM=[
        ('Projet','Projet'),
        ('Mission','Mission'),
    ]
    projet_mission=models.CharField(max_length=100, null=True, choices=PM)
    tache=models.CharField(max_length=300)
    date_debut=models.DateField(null=True)
    date_fin=models.DateField(null=True)
    status=models.BooleanField(null=True,default=False)
    title=models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.type_exp

