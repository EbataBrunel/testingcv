from django.urls import path
from .views import*
from django.conf.urls import handler404, handler500

urlpatterns=[
    path("", dashboard, name="dashboard"),
    path("annees", annees, name="annee/annees"),
    path("add-annee", add_annee, name="annee/add_annee"),
    path("edit-annee/<int:id>", edit_annee, name="annee/edit_annee"),
    path("edit-an", edit_an, name="annee/edit_an"),
    path("del-annee/<int:id>", del_annee, name="annee/del_annee"),

    path("contact", contact, name="contact/contact"),
    path("contacts", contacts, name="contact/contacts"),
    path("del-contact/<int:id>", del_contact, name="contact/del_contact"),
    path("delete-contact/<int:id>", delete_contact, name="contact/delete_contact"),
    path("del-message/<int:id>", del_message, name="contact/del_message"),
    #path("delete_messages/<int:id>", delete_messages, name="contact/delete_messages"),
    path("details-contact/<str:id>", details_contact, name="contact/details_contact"),
    path("contactuser/<int:id>", contactuser, name="contact/contactuser"),
    path("contuser", contuser, name="contact/contuser"),
    path("messages", messag, name="contact/messages"),
    path("detmes/<int:id>", detmes, name="contact/detmes"),
    path("apropos", apropos, name="contact/apropos"),
    path("services", services, name="contact/services"),

    path("etablissements", etablissements, name="etablissement/etablissements"),
    path("add-etab", add_etab, name="etablissement/add_etab"),
    path("edit-etab/<int:id>", edit_etab, name="etablissement/edit_etab"),
    path("edit-eta", edit_eta, name="etablissement/edit_eta"),
    path("del-etab/<int:id>", del_etab, name="etablissement/del_etab"),

    path("formations", formations, name="formation/formations"),
    path("add-form", add_form, name="formation/add_form"),
    path("edit-form/<int:id>", edit_form, name="formation/edit_form"),
    path("edit-for", edit_for, name="formation/edit_for"),
    path("del-form/<int:id>", del_form, name="formation/del_form"),

    path("entreprises", entreprises, name="entreprise/entreprises"),
    path("add-ent", add_ent, name="entreprise/add_ent"),
    path("edit-ent/<int:id>", edit_ent, name="entreprise/edit_ent"),
    path("edit-ent", edit_en, name="entreprise/edit_en"),
    path("del-ent/<int:id>", del_ent, name="entreprise/del_ent"),

    path("parcours", parcours, name="parcours/parcours"),
    path("add-parcours", add_parcours, name="parcours/add_parcours"),
    path("del-parcours/<int:id>", del_parcours, name="parcours/del_parcours"),
    path("edit-parcours/<int:id>", edit_parcours, name="parcours/edit_parcours"),
    path("edit-par", edit_par, name="parcours/edit_par"),
    path("statpar/<int:id>", statpar.as_view(), name="parcours/statpar"),
    path("fetchpar/<int:id>", fetchpar.as_view(), name="fetchpar"),
    path("status/<str:id>", status.as_view(), name="status"),

    path("maintenance", maintenance, name="maintenance"),
    path("statistique", statistique, name="statistique"),
    path("authorization", authorization, name="authorization"),
    path("recap", recap, name="cv/recap"),
    path("recap-1", recap_1, name="cv/recap-1"),
    path("cv/<int:id>", cv, name="cv/cv"),
    path("profuser/<int:id>", profuser, name="cv/profuser"),
    path("generatecv", generatecv, name="cv/generatecv"),
    path("generatecv-1", generatecv_1, name="cv/generatecv-1"),


    path("competences", competences, name="competence/competences"),
    path("details-comp/<str:id>", details_comp, name="competence/details_comp"),
    path("add-comp", add_comp, name="competence/add_comp"),
    path("edit-comp/<int:id>", edit_comp, name="competence/edit_comp"),
    path("edit-cmp", edit_cmp, name="competence/edit_cmp"),
    path("del-comp/<int:id>", del_comp, name="competence/del_comp"),
    path("delete-comp/<str:id>", delete_comp, name="delete_comp"),
    path("details-comp/statcomp/<int:id>", statcomp.as_view(), name="statcomp"),
    path("fetchcomp/<str:id>", fetchcomp.as_view(), name="fetchcomp"),
    path("ajaxcomp/<str:id>", ajaxcomp.as_view(), name="ajaxcomp"),

    path("experiences", experiences, name="experience/experiences"),
    path("add-exp", add_exp, name="experience/add_exp"),
    path("del-exp/<int:id>", del_exp, name="experience/del_exp"),
    path("edit-exp/<int:id>", edit_exp, name="experience/edit_exp"),
    path("edit-ex", edit_ex, name="experience/edit_ex"),
    path("statexp/<int:id>", statexp.as_view(), name="experience/statexp"),

    path("ajax/<str:id>", getFormParcours.as_view(), name="ajax"),
    path("edit-exp/ajax/<str:id>", getFormParcours2.as_view(), name="ajax"),
    path("ajaxAnnee/<int:id>", getFormAnnee.as_view(), name="ajaxAnnee"),
    path("edit-parcours/ajaxAnnee/<int:id>", getFormAnnee2.as_view(), name="ajaxAnnee")

]

handler404 = "eab.views.handler404"
handler500 = "eab.views.handler500"


