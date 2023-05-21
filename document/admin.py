from django.contrib import admin
from .models import*

class AdminCours(admin.ModelAdmin):
    list_display=('id','user','composant')
    search_fields=('user',)

class AdminPanier(admin.ModelAdmin):
    list_display=('id','user')
    search_fields=('user',)

class AdminCommande(admin.ModelAdmin):
    list_display=('id','user')
    search_fields=('user',)

admin.site.register(Cours, AdminCours)
admin.site.register(Panier, AdminPanier)
admin.site.register(Commande, AdminCommande)
