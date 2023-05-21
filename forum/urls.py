from django.urls import path
from .views import*

urlpatterns=[

    path("disciplines", disciplines, name="discipline/disciplines"),
    path("add-disc", add_disc, name="discipline/add_disc"),
    path("edit-disc/<int:id>", edit_disc, name="discipline/edit_disc"),
    path("edit-dis", edit_dis, name="discipline/edit_dis"),
    path("del-disc/<int:id>", del_disc, name="discipline/del_disc"),

    path("composants", composants, name="composant/composants"),
    path("add-cmp", add_cmp, name="composant/add_cmp"),
    path("edit-cmp/<int:id>", edit_cmp, name="composant/edit_cmp"),
    path("edit-com", edit_com, name="composant/edit_com"),
    path("del-comp/<int:id>", del_cmp, name="del_cmp"),
    path("details_cmp/<int:id>", details_cmp, name="composant/details_cmp"),

    path("postquestion", postquestion, name="question/postquestion"),
    path("questions", questions, name="question/questions"),
    path("my-questions", my_questions, name="question/my_questions"),
    path("ajaxCompDisc/<int:id>", getCompDiscipline.as_view(), name="ajaxCompDisc"),
    path("fetchq/<int:id>", fetchq.as_view(), name="fetchq"),
    path("del-ques/<int:id>", delquestion, name="del_ques"),
    path("my-delques/<int:id>", my_delques, name="my-delques"),
    path("f-delques/<int:id>", f_delques, name="f-delques"),

    path("answer/<int:id>", answer, name="question/answer"),
    path("f-answer/<int:id>", f_answer, name="question/f-answer"),
    path("my-answer/<int:id>", my_answer, name="question/my-answer"),
    path("del-answer/<int:id>", delanswer, name="del-answer"),
    path("my-delanswer/<int:id>",my_delanswer, name="my-delanswer"),
    path("f-delanswer/<int:id>",f_delanswer, name="f-delanswer"),
    path("listforum", listforum, name="question/listforum"),
    path("detforum/<int:id>", detforum, name="question/detforum"),
    path("ajaxlike/<int:id>", ajaxlike.as_view(), name="ajaxlike"),
    path("ajaxlikes/<int:id>", ajaxlikes.as_view(), name="ajaxlikes"),
    path("answer/ajaxlike/<int:id>", ajaxlikeanswer.as_view(), name="ajaxlike"),
    path("answer/ajaxlikes/<int:id>", ajaxlikeanswers.as_view(), name="ajaxlikes"),
    path("f-answer/ajaxlikes/<int:id>", ajaxlikeanswers.as_view(), name="ajaxlikes"),
    path("my-answer/ajaxlikes/<int:id>", ajaxlikeanswers.as_view(), name="ajaxlikes"),
    path("detforum/ajaxlike/<int:id>", ajaxlike.as_view(), name="ajaxlike"),
    path("detforum/ajaxlikes/<int:id>", ajaxlikes.as_view(), name="ajaxlikes")
]
