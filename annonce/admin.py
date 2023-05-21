from django.contrib import admin
from .models import*

class AdminAnnonce(admin.ModelAdmin):
    list_display=('id','user','title','company')
    search_fields=('user',)

admin.site.register(Annonce, AdminAnnonce)
