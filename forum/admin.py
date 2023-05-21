from django.contrib import admin
from .models import*

class AdminDiscipline(admin.ModelAdmin):
    list_display=('id','libelle')
    search_fields=('libelle',)

class AdminComposant(admin.ModelAdmin):
    list_display=('id','discipline','libelle')
    search_fields=('libelle',)

class AdminQuestion(admin.ModelAdmin):
    list_display=('id','user','discipline','composant')
    search_fields=('user',)

class AdminAnswer(admin.ModelAdmin):
    list_display=('id','user','question')
    search_fields=('user',)


admin.site.register(Discipline, AdminDiscipline)
admin.site.register(Composant, AdminComposant)
admin.site.register(Question, AdminQuestion)
admin.site.register(Answer, AdminAnswer)