from django.urls import path
from .views import*

urlpatterns=[
    path("annonces", annonces, name="annonce/annonces"),
    path("annonce", annonce, name="annonce/annonce"),
    path("add-annonce", add_annonce, name="annonce/add-annonce"),
     path("edit-annonce/<int:id>", edit_annonce, name="annonce/edit-annonce"),
    path("edit-ann", edit_ann, name="annonce/edit-ann"),
    path("del-annonce/<int:id>", del_annonce, name="del-annonce"),
    path("delete-annonce/<int:id>", delete_annonce, name="delete-annonce") 
]