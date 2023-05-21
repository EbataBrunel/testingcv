from django.urls import path
from .views import*

urlpatterns=[
    path("cours", cours, name="cours/cours"),
    path("listcours", listcours, name="cours/listcours"),
    path("detcours/<int:id>",detcours, name="cours/detcours"),
    path("dcours/<int:id>",dcours, name="cours/dcours"),
    path("v-cours/<int:id>",viewcours, name="cours/v-cours"),
    path("details/<int:id>", details, name="cours/details"),
    path("mescours", mescours, name="cours/mescours"),
    path("d-cours/<int:id>", d_cours, name="cours/d-cours"),
    path("details-cours/<int:id>", details_cours, name="cours/details-cours"),
    path("add-cours", add_cours, name="cours/add_cours"),
    path("edit-cours/<int:id>", edit_cours, name="cours/edit_cours"),
    path("doc-pur", doc_purchased, name="commande/doc-pur"),
    path("my-docpur", my_doc_purchased, name="commande/my-docpur"),
    path("delcours/<int:id>", delcours, name="delcours"),
    path("del-cours/<int:id>", del_cours, name="del_cours"),
    path("delete-cours/<int:id>", delete_cours, name="delete_cours"),
    path("delcourscmp/<int:id>", delcourscmp, name="delcourscmp"),
    path("deldocdiscipline/<int:id>", deldocdisiscipline, name="deldocdiscipline"),
    path("deldoccomposant/<int:id>", deldoccomposant, name="deldoccomposant"),

    path("c-encours", coursencours, name="cours/c-encours"),
    path("dc-encours/<int:id>", detcoursencours, name="cours/detcoursencours"),
    path("d-encours/<int:id>", dcoursencours, name="cours/dcoursencours"),

    path("cours-pub", courspub, name="cours/courspub"),
    path("detcourspub/<int:id>", detcourspub, name="cours/detcourspub"),
    path("dc-pub/<int:id>", dcourspub, name="cours/dcourspub"),

    path("c-nonpub", coursnonpub, name="cours/coursnonpub"),
    path("dc-nonpub/<int:id>", detcoursnonpub, name="cours/detcoursnonpub"),
    path("d-nonpub/<int:id>", dcoursnonpub, name="cours/dcoursnonpub"),

    path("ajaxCompDisc/<int:id>", getCompDiscipline.as_view(), name="ajaxCompDisc"),
    path("ajaxType/<str:id>", getPrice.as_view(), name="ajaxType"),
    path("edit-cours/ajaxType/<str:id>", getPrice.as_view(), name="ajaxType"),
    path("edit-cours/ajaxCompDisc/<int:id>", getCompDiscipline.as_view(), name="ajaxCompDisc"),
    path("ajaxCours/<int:id>", getCours.as_view(), name="ajaxCours"),

    path("addPanier/<int:id>", addPanier.as_view(), name="addPanier"),
    path("details/addPanier/<int:id>", addPanier.as_view(), name="addPanier"),
    path("panier", panier, name="commande/panier"),
    path("delpanier/<int:id>", del_panier, name="commande/del_panier"),
    path("paiement", paiement, name="commande/paiement"),
    path("validecmd", validecmd, name="commande/validecmd"),
    path("success", success, name="commande/success"),
    path("echec", echec, name="commande/echec"),
    path("commandes", commandes, name="commande/commandes"),
    path("delachat/<int:id>", delachat, name="commande/delachat"),
    path("detachat/<int:id>", detachat, name="commande/detachat"),
    path("facture/<int:id>", facture, name="commande/facture"),

    path("fetchdoccmp/<int:id>", fetchdoc.as_view(), name="fetchdoc"),
    path("detcours/fetchdoccmp/<int:id>", fetchdoccmp.as_view(), name="fetchdoccmp")
]