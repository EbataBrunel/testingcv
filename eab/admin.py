from django.contrib import admin
from .models import*

admin.site.site_header="EAJC"
admin.site.site_title="CV"
admin.site.index_title="EAJC"

class AdminProfile(admin.ModelAdmin):
    list_display=('user','phone','address')
    search_fields=('user',)

class AdminAnnee(admin.ModelAdmin):
    search_fields=('libelle',)

class AdminContact(admin.ModelAdmin):
    list_display=('datecontact','name','email','statut')
    search_fields=('name',)

class AdminEtablissement(admin.ModelAdmin):
    list_display=('name','country','city')
    search_fields=('name',)

class AdminFormation(admin.ModelAdmin):
    search_fields=('intitule',)

class AdminParcours(admin.ModelAdmin):
    list_display=('etablissement','formation','niveau')

class AdminCompetence(admin.ModelAdmin):
    list_display=('type_comp','name','user')
    search_fields=('type_comp',)

class AdminExperience(admin.ModelAdmin):
    list_display=('type_exp','entreprise','user')
    search_fields=('type_exp',)

admin.site.register(Profile, AdminProfile)
admin.site.register(Annee, AdminAnnee)
admin.site.register(Contact, AdminContact)
admin.site.register(Etablissement, AdminEtablissement)
admin.site.register(Formation, AdminFormation)
admin.site.register(Parcours, AdminParcours)
admin.site.register(Competence, AdminCompetence)
admin.site.register(Experience, AdminExperience)
admin.site.register(Parametre)
