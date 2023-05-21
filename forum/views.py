from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from eab.views import*
from eab.models import*
from app_auth.decorator import*
from .models import*
from .forms import*
import datetime

def new_message( request):
    #Lecture des messages reçus
    contacts=Contact.objects.filter(statut=0, status=1).order_by("-id")
    tabUsers=[]
    tabIdUser=[]
    for contact in contacts:
        #Convertion d'un string en dictionnaire
        diccode=eval(contact.codes)
        #On verifie s'il est le recepteur du message
        if diccode["user1"]==request.user.id:
            dic={}
            tabIdUser.append(diccode["user2"])

            us=User.objects.get(id=diccode["user2"])

            dic["id"]=us.id
            dic["lastname"]=us.last_name
            dic["firstname"]=us.first_name
            dic["message"]=contact.message
            dic["date"]=contact.datecontact
            dic["photo"]=us.profile.photo
            tabUsers.append(dic)

    #On elemine des identifiants qui se dupliquent
    tab=[]
    for i in tabIdUser:
        if i not in tab:
            tab.append(i)
    #On compte le nombre de messages envoyés par chaque membre
    dic={}
    for i in tab:
        nombre=0
        for k in tabIdUser:
            if i==k:
                nombre=nombre+1
        dic[i]=nombre

    tabMessages=[]
    tabs=[]
    for k,v in dic.items():
        for cont in tabUsers:
            if cont["id"]==i:
                if i not in tabs:
                    cont["nombre"]=v
                    tabMessages.append(cont)
                    tabs.append(i)
    return tabMessages

def nbnew_message(request):
    #On compte le nombre total de message reçus
    contacts=Contact.objects.filter(statut=0, status=1).order_by("-id")
    count=0
    for contact in contacts:
        #Convertion d'un string en dictionnaire
        diccode=eval(contact.codes)
        if diccode["user1"]==request.user.id:
            count=count+1
    return count

#On determine le nombre des reponses non lu des questions du membre connecté
def nbnew_answer(request):
    questions=Question.objects.filter(user_id=request.user.id)
    number=0
    for question in questions:
        answers=Answer.objects.filter(question_id=question.id, status=0)
        #On exlu les reponses de ce membre qui a posé la question
        for answer in answers:
            if answer.user_id != request.user.id:
                number+=1
    return number


#=================== Gestion de discipline ======================
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def disciplines(request):
    date=datetime.datetime.now()

    disciplines=Discipline.objects.all()
    context={
        "disciplines":disciplines,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "discipline/disciplines.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_disc(request):
    date=datetime.datetime.now()
    if request.method=="POST":
        libelle=request.POST["libelle"]
        query=Discipline.objects.filter(libelle=libelle)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            discipline=Discipline(libelle=libelle)
            count0=Discipline.objects.all().count()
            discipline.save()
            count1=Discipline.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
                return JsonResponse({'status':1})
    context={
        "parametre":parametre(), 
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
        }
    return render(request, "discipline/add_disc.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_disc(request,id):
    date=datetime.datetime.now()
    discipline=Discipline.objects.get(id=id)
    context={
        "discipline":discipline,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "discipline/edit_disc.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def edit_dis(request):
    
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            discipline=Discipline.objects.get(id=id)
        except:
            discipline=None

        if discipline == None:
            return JsonResponse({'status':1})
        else:
            libelle=request.POST["libelle"]
            #On verifie si cette année a déjà été enregistrée
            disciplines=Discipline.objects.exclude(id=id)
            tabDiscipline=[]
            for disc in disciplines:          
                tabDiscipline.append(disc.libelle)
            #On verifie si cette année existe déjà
            if libelle in tabDiscipline:
                return JsonResponse({"status":0}) 
            else:
                discipline.libelle=libelle
                discipline.save()
                return JsonResponse({'status':'Save'})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def del_disc(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)
    if request.method=="POST":
        discipline.delete()
        return redirect("discipline/disciplines")
    context={
        "discipline":discipline,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "discipline/del_disc.html", context)

#=================== Gestion du composant ======================
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def composants(request):
    date=datetime.datetime.now()

    tabComposants=[]
    #On regroupe des composant par disciplines
    composants=Composant.objects.values("discipline_id").annotate(effectif=Count("discipline_id"))
    for composant in composants:
    	#On recupère la discipline
        discipline=Discipline.objects.get(id=composant["discipline_id"])
        dic={}
        dic["id"]=discipline.id
        dic["libelle"]=discipline.libelle
        dic["effectif"]=composant["effectif"]

        tabComposants.append(dic)
    context={
        "composants":tabComposants,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "composant/composants.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def details_cmp(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)
    composants=Composant.objects.filter(discipline_id=id)
    context={
    	"discipline":discipline,
        "composants":composants,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "composant/details_cmp.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def add_cmp(request):
    date=datetime.datetime.now()
    if request.method=="POST":
        libelle=request.POST["libelle"]
        discipline=request.POST["discipline"]
        query=Composant.objects.filter(libelle=libelle)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            composant=Composant(libelle=libelle, discipline_id=discipline)
            count0=Composant.objects.all().count()
            composant.save()
            count1=Composant.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
                return JsonResponse({'status':1})
            
    disciplines=Discipline.objects.all()
    context={
        "disciplines":disciplines, 
        "parametre":parametre(), 
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "composant/add_cmp.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_cmp(request,id):
    date=datetime.datetime.now()
    composant=Composant.objects.get(id=id)
    disciplines=Discipline.objects.all()
    context={
        "composant":composant,
        "disciplines":disciplines,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "composant/edit_cmp.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def edit_com(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            composant=Composant.objects.get(id=id)
        except:
            composant=None

        if composant == None:
            return JsonResponse({'status':1})
        else:
            libelle=request.POST["libelle"]
            discipline=request.POST["discipline"]
            #On verifie si cette année a déjà été enregistrée
            composants=Composant.objects.exclude(id=id)
            tabComposant=[]
            for comp in composants:          
                tabComposant.append(comp.libelle)
            #On verifie si cette année existe déjà
            if libelle in tabComposant:
                return JsonResponse({"status":0}) 
            else:
                composant.libelle=libelle
                composant.discipline_id=discipline
                composant.save()
                return JsonResponse({'status':'Save'})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def del_cmp(request,id):
    composant=Composant.objects.get(id=id)
    composant.delete()
    return redirect("composant/details_cmp", id=composant.discipline_id)


#======================== Questions & Reponses===================
@login_required(login_url='login')
def postquestion(request):
    date=datetime.datetime.now()

    if request.method=="POST":        
        form=QuestionForm(request.POST)
        if form.is_valid():
            user=request.user.id
            discipline=request.POST["discipline"]
            composant=request.POST["composant"]
            subject=request.POST["subject"]
            content=form.cleaned_data["content"]

            question=Question(
            	subject=subject, 
            	content=content, 
            	date=date, 
            	composant_id=composant, 
            	discipline_id=discipline, 
            	user_id=user)
            question.save()

            #messages.error(request, "Message envoyé avec succès.")
            return redirect("question/questions")
        else:
            form=QuestionForm()

    disciplines=Discipline.objects.all()
    form=QuestionForm()
    context={
    	"disciplines":disciplines,
    	"form":form,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/postquestion.html", context)

class getCompDiscipline(View):
    def get(self, request, id, *args, **kwargs):
        
        composants=Composant.objects.filter(discipline_id=id)

        context={
            "composants":composants
        }
        return render(request, "ajaxCompDisc.html", context)
    
@login_required(login_url='login')
def questions(request):
    date=datetime.datetime.now()

    questions=Question.objects.all().order_by("-id")
    tabQuestion=[]
    
    for ques in questions:
        status=0
        #On determine le nombre de likes de chaque question
        countlikes=Likes.objects.filter(question_id=ques.id).count()
        #On verifie le membre connecté a déjà liké ou pas
        q=Likes.objects.filter(question_id=ques.id,user_id=request.user.id)
        if q.exists():
            status+=1

        quests=Answer.objects.values("question_id").filter(question_id=ques.id).annotate(effectif=Count("question_id"))
        if quests.exists():
            for quest in quests:
                question=Question.objects.get(id=quest["question_id"])
                dic={}
                dic["id"]=quest["question_id"]
                dic["subject"]=question.subject
                dic["content"]=question.content
                dic["date"]=question.date
                dic["username"]=question.user.username
                dic["user_id"]=question.user.id
                try:
                    dic["photo"]=question.user.profile.photo
                except:
                    dic["photo"]=None
                dic["composant"]=question.composant.libelle
                dic["effectif"]=quest["effectif"]
                dic["countlikes"]=countlikes
                dic["status"]=status
                tabQuestion.append(dic)
        else:
            dic={}
            dic["id"]=ques.id
            dic["subject"]=ques.subject
            dic["content"]=ques.content
            dic["date"]=ques.date
            dic["username"]=ques.user.username
            dic["user_id"]=ques.user.id
            try:
                dic["photo"]=ques.user.profile.photo
            except:
                dic["photo"]=None
            dic["composant"]=ques.composant.libelle
            dic["effectif"]=0
            dic["countlikes"]=countlikes
            dic["status"]=status
            tabQuestion.append(dic)

    paginator = Paginator(tabQuestion, 10)
    num_page=request.GET.get('page')
    tabQuestion=paginator.get_page(num_page)
    
    context={
    	"questions":tabQuestion,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
        }
    return render(request, "question/questions.html", context)

@login_required(login_url='login')
def my_questions(request):
    date=datetime.datetime.now()
    #On change de statut pour marquer la reception de notification sur des nouvelles reponses aux questions de ce memebre
    quest=Question.objects.filter(user_id=request.user.id).order_by("-id")
    for question in quest:
        answers=Answer.objects.filter(question_id=question.id, status=0)
        for answer in answers:
            answ=answer
            answ.status=1
            answ.save()

    questions=Question.objects.filter(user_id=request.user.id).order_by("-id")
    tabQuestion=[]
    for ques in questions:

        status=0
        #On determine le nombre de likes de chaque question
        countlikes=Likes.objects.filter(question_id=ques.id).count()
        #On verifie le membre connecté a déjà liké ou pas
        q=Likes.objects.filter(question_id=ques.id,user_id=request.user.id)
        if q.exists():
            status+=1

        quests=Answer.objects.values("question_id").filter(question_id=ques.id).annotate(effectif=Count("question_id"))
        if quests.exists():
            for quest in quests:
                #On compte le nombre de reponses non lus
                list_answers=Answer.objects.filter(question_id=ques.id, status=1)
                #On exlu les reponses de ce membre qui a posé la question
                countanswer=0
                for answer in list_answers:
                    if answer.user_id != request.user.id:
                        countanswer+=1

                question=Question.objects.get(id=quest["question_id"])
                dic={}
                dic["id"]=quest["question_id"]
                dic["q"]=question
                dic["subject"]=question.subject
                dic["content"]=question.content
                dic["date"]=question.date
                dic["username"]=question.user.username
                dic["user_id"]=ques.user.id
                try:
                    dic["photo"]=ques.user.profile.photo
                except:
                    dic["photo"]=None
                dic["effectif"]=quest["effectif"]
                dic["countanswer"]=countanswer
                dic["countlikes"]=countlikes
                dic["status"]=status
                tabQuestion.append(dic)
        else:
            dic={}
            dic["id"]=ques.id
            dic["q"]=question
            dic["subject"]=ques.subject
            dic["content"]=ques.content
            dic["date"]=ques.date
            dic["username"]=ques.user.username
            dic["user_id"]=ques.user.id
            try:
                dic["photo"]=ques.user.profile.photo
            except:
                dic["photo"]=None
            dic["effectif"]=0
            dic["countanswer"]=0
            dic["countlikes"]=countlikes
            dic["status"]=status
            tabQuestion.append(dic)

    paginator = Paginator(tabQuestion, 10)
    num_page=request.GET.get('page')
    tabQuestion=paginator.get_page(num_page)
    
    context={
    	"questions":tabQuestion,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/my_questions.html", context)

@login_required(login_url='login')
def answer(request,id):
    date=datetime.datetime.now()
    #On recupère la question
    question=Question.objects.get(id=id)
    #On change le statut de cette question pour marquer quen toutes ses reponses ont été lu
    answers=Answer.objects.filter(question_id=id, status=1)
    for answer in answers:
            answ=answer
            answ.status=2
            answ.save()
    
    if request.method=="POST":        
        form=AnswerForm(request.POST)
        if form.is_valid():
            user=request.user.id
            content=form.cleaned_data["content"]

            answer=Answer(
            	content=content, 
            	date=date, 
            	question_id=id,
            	user_id=user)
            answer.save()

            #messages.error(request, "Message envoyé avec succès.")
            return redirect("question/answer", id=id)
        else:
            form=AnswerForm()

    answers=Answer.objects.filter(question_id=id).order_by("-id")
    #On determine l'ordre de chaque question
    tabanswer=[]
    count=0
    for answer in answers:

        status=0
        #On determine le nombre de likes de chaque réponse
        countlikes=Likeanswer.objects.filter(answer_id=answer.id).count()
        #On verifie si le membre connecté a déjà liké ou pas chaque réponse
        q=Likeanswer.objects.filter(answer_id=answer.id,user_id=request.user.id)
        if q.exists():
            status+=1

        count+=1
        dic={}
        dic["id"]=answer.id
        try:
            dic["photo"]=answer.user.profile.photo
        except:
            dic["photo"]=None
        dic["content"]=answer.content
        dic["user_id"]=answer.user.id
        dic["username"]=answer.user.username
        dic["date"]=answer.date
        dic["usernameauthor"]=answer.question.user.username
        dic["composant"]=answer.question.composant.libelle
        dic["count"]=count
        dic["countlikes"]=countlikes
        dic["status"]=status
        tabanswer.append(dic)

    totalanswer=answers=Answer.objects.filter(question_id=id).count()

    form=AnswerForm()
    context={
        "totalanswer":totalanswer,
        "question":question,
    	"answers":tabanswer,
    	"form":form,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/answer.html", context)

@login_required(login_url='login')
def f_answer(request,id):
    date=datetime.datetime.now()
    #On recupère la question
    question=Question.objects.get(id=id)
    #On change le statut de cette question pour marquer quen toutes ses reponses ont été lu
    answers=Answer.objects.filter(question_id=id, status=1)
    for answer in answers:
            answ=answer
            answ.status=2
            answ.save()
    
    if request.method=="POST":        
        form=AnswerForm(request.POST)
        if form.is_valid():
            user=request.user.id
            content=form.cleaned_data["content"]

            answer=Answer(
            	content=content, 
            	date=date, 
            	question_id=id,
            	user_id=user)
            answer.save()

            #messages.error(request, "Message envoyé avec succès.")
            return redirect("question/f-answer", id=id)
        else:
            form=AnswerForm()

    answers=Answer.objects.filter(question_id=id).order_by("-id")
    #On determine l'ordre de chaque question
    tabanswer=[]
    count=0
    for answer in answers:

        status=0
        #On determine le nombre de likes de chaque réponse
        countlikes=Likeanswer.objects.filter(answer_id=answer.id).count()
        #On verifie si le membre connecté a déjà liké ou pas chaque réponse
        q=Likeanswer.objects.filter(answer_id=answer.id,user_id=request.user.id)
        if q.exists():
            status+=1

        count+=1
        dic={}
        dic["id"]=answer.id
        try:
            dic["photo"]=answer.user.profile.photo
        except:
            dic["photo"]=None
        dic["content"]=answer.content
        dic["user_id"]=answer.user.id
        dic["username"]=answer.user.username
        dic["date"]=answer.date
        dic["usernameauthor"]=answer.question.user.username
        dic["composant"]=answer.question.composant.libelle
        dic["count"]=count
        dic["countlikes"]=countlikes
        dic["status"]=status
        tabanswer.append(dic)

    totalanswer=answers=Answer.objects.filter(question_id=id).count()

    form=AnswerForm()
    context={
        "totalanswer":totalanswer,
        "question":question,
    	"answers":tabanswer,
    	"form":form,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/f-answer.html", context)

@login_required(login_url='login')
def my_answer(request,id):
    date=datetime.datetime.now()
    #On recupère la question
    question=Question.objects.get(id=id)
    #On change le statut de cette question pour marquer quen toutes ses reponses ont été lu
    answers=Answer.objects.filter(question_id=id, status=1)
    for answer in answers:
            answ=answer
            answ.status=2
            answ.save()
    
    if request.method=="POST":        
        form=AnswerForm(request.POST)
        if form.is_valid():
            user=request.user.id
            content=form.cleaned_data["content"]

            answer=Answer(
            	content=content, 
            	date=date, 
            	question_id=id,
            	user_id=user)
            answer.save()

            #messages.error(request, "Message envoyé avec succès.")
            return redirect("question/my-answer", id=id)
        else:
            form=AnswerForm()

    answers=Answer.objects.filter(question_id=id).order_by("-id")
    #On determine l'ordre de chaque question
    tabanswer=[]
    count=0
    for answer in answers:

        status=0
        #On determine le nombre de likes de chaque réponse
        countlikes=Likeanswer.objects.filter(answer_id=answer.id).count()
        #On verifie si le membre connecté a déjà liké ou pas chaque réponse
        q=Likeanswer.objects.filter(answer_id=answer.id,user_id=request.user.id)
        if q.exists():
            status+=1

        count+=1
        dic={}
        dic["id"]=answer.id
        try:
            dic["photo"]=answer.user.profile.photo
        except:
            dic["photo"]=None
        dic["content"]=answer.content
        dic["user_id"]=answer.user.id
        dic["username"]=answer.user.username
        dic["date"]=answer.date
        dic["usernameauthor"]=answer.question.user.username
        dic["composant"]=answer.question.composant.libelle
        dic["count"]=count
        dic["countlikes"]=countlikes
        dic["status"]=status
        tabanswer.append(dic)

    totalanswer=answers=Answer.objects.filter(question_id=id).count()

    form=AnswerForm()
    context={
        "totalanswer":totalanswer,
        "question":question,
    	"answers":tabanswer,
    	"form":form,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/my-answer.html", context)

@login_required(login_url='login')
def listforum(request):
    date=datetime.datetime.now()

    disciplines=Discipline.objects.all()
    tabDicsipline=[]
    for discipline in disciplines:
        dicDisc={}
        effect=0
        composants=Composant.objects.filter(discipline_id=discipline.id)
        tabComposants=[]
        for composant in composants:
            query=Question.objects.values("composant_id").filter(composant_id=composant.id).annotate(effectif=Count("composant_id"))
            if query.exists():
                for comp in query:
                    effect+=comp["effectif"]
                    dic={}
                    dic["id"]=composant.id
                    dic["libelle"]=composant.libelle
                    dic["effectif"]=comp["effectif"]
                    tabComposants.append(dic)
            else:
                dic={}
                dic["id"]=composant.id
                dic["libelle"]=composant.libelle
                dic["effectif"]=0
                tabComposants.append(dic)

        dicDisc["id"]=discipline.id
        dicDisc["libelle"]=discipline.libelle
        dicDisc["effectif"]=effect
        dicDisc["composants"]=tabComposants
        tabDicsipline.append(dicDisc)

    paginator = Paginator(tabDicsipline, 10)
    num_page=request.GET.get('page')
    tabDicsipline=paginator.get_page(num_page)

    context={
            "disciplines":tabDicsipline,
            "parametre":parametre(),
            "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/listforum.html", context)

@login_required(login_url='login')
def detforum(request,id):
    date=datetime.datetime.now()
    composant=Composant.objects.get(id=id)
    questions=Question.objects.filter(composant_id=id).order_by("-id")
    tabQuestion=[]
    for ques in questions:
        status=0
        #On determine le nombre de likes de chaque question
        countlikes=Likes.objects.filter(question_id=ques.id).count()
        #On verifie le membre connecté a déjà liké ou pas
        q=Likes.objects.filter(question_id=ques.id,user_id=request.user.id)
        if q.exists():
            status+=1

        quests=Answer.objects.values("question_id").filter(question_id=ques.id).annotate(effectif=Count("question_id"))
        if quests.exists():
            for quest in quests:
                question=Question.objects.get(id=quest["question_id"])
                dic={}
                dic["q"]=question
                dic["id"]=quest["question_id"]
                dic["subject"]=question.subject
                dic["content"]=question.content
                dic["date"]=question.date
                dic["username"]=question.user.username
                dic["user_id"]=question.user.id
                try:
                    dic["photo"]=question.user.profile.photo
                except:
                    dic["photo"]=None
                dic["effectif"]=quest["effectif"]
                dic["countlikes"]=countlikes
                dic["status"]=status
                tabQuestion.append(dic)
        else:
            dic={}
            dic["q"]=ques
            dic["id"]=ques.id
            dic["subject"]=ques.subject
            dic["content"]=ques.content
            dic["date"]=ques.date
            dic["username"]=ques.user.username
            dic["user_id"]=ques.user.id
            try:
                dic["photo"]=ques.user.profile.photo
            except:
                dic["photo"]=None
            dic["effectif"]=0
            dic["countlikes"]=countlikes
            dic["status"]=status
            tabQuestion.append(dic)

    paginator = Paginator(tabQuestion, 10)
    num_page=request.GET.get('page')
    tabQuestion=paginator.get_page(num_page)
    
    context={
        "composant":composant,
    	"questions":tabQuestion,
    	"parametre":parametre(),
    	"date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "question/detfurom.html", context)


class ajaxlike(View):
    def get(self, request, id, *args, **kwargs):
        status=0
        query=Likes.objects.filter(question_id=id,user_id=request.user.id)
        if query.exists():
            for like in query:
                like.delete()
        else:
            like=Likes(question_id=id, user_id=request.user.id)
            like.save()

            q=Likes.objects.filter(question_id=id,user_id=request.user.id)
            if q.exists():
                status+=1

        #On compte le nombre de likes
        countlikes=Likes.objects.filter(question_id=id).count()
        #Liste des membres qui ont likés cette question
        likes=Likes.objects.filter(question_id=id)

        context={
            "id":id,
            "status":status,
            "countlikes":countlikes,
            "likes":likes
        }
        return render(request, "ajaxlike.html", context)
    
class ajaxlikes(View):
    def get(self, request, id, *args, **kwargs):
        #Liste des membres qui ont likés cette question
        likes=Likes.objects.filter(question_id=id).order_by("-id")
        countlikes=Likes.objects.filter(question_id=id).count()
        context={
            "likes":likes,
            "countlikes":countlikes
        }
        return render(request, "ajaxlikes.html", context)
    
class ajaxlikeanswer(View):
    def get(self, request, id, *args, **kwargs):
        status=0
        query=Likeanswer.objects.filter(answer_id=id,user_id=request.user.id)
        if query.exists():
            for likeanswer in query:
                likeanswer.delete()
        else:
            likeanswer=Likeanswer(answer_id=id, user_id=request.user.id)
            likeanswer.save()

            q=Likeanswer.objects.filter(answer_id=id,user_id=request.user.id)
            if q.exists():
                status+=1

        #On compte le nombre de likes
        countlikes=Likeanswer.objects.filter(answer_id=id).count()

        context={
            "status":status,
            "countlikes":countlikes
        }
        return render(request, "ajaxlike.html", context)
    
class ajaxlikeanswers(View):
    def get(self, request, id, *args, **kwargs):
        #Liste des membres qui ont likés cette question
        likes=Likeanswer.objects.filter(answer_id=id).order_by("-id")
        #On compte le nombre de likes
        countlikes=Likeanswer.objects.filter(answer_id=id).count()

        context={
            "likes":likes,
            "countlikes":countlikes
        }
        return render(request, "ajaxlikes.html", context)
    
class fetchq(View):
    def get(self, request, id, *args, **kwargs):
        return render(request, "fetchq.html", {"id":id}) 
    
def delquestion(request,id):
    question=Question.objects.get(id=id)
    question.delete()
    return redirect("question/questions")

def my_delques(request,id):
    question=Question.objects.get(id=id)
    question.delete()
    return redirect("question/my_questions")

def f_delques(request,id):
    question=Question.objects.get(id=id)
    question.delete()
    return redirect("question/detforum", question.composant.id)

def delanswer(request,id):
    answer=Answer.objects.get(id=id)
    answer.delete()
    return redirect("question/answer", id=answer.question.id)

def my_delanswer(request,id):
    answer=Answer.objects.get(id=id)
    answer.delete()
    return redirect("question/my-answer", id=answer.question.id)

def f_delanswer(request,id):
    answer=Answer.objects.get(id=id)
    answer.delete()
    return redirect("question/f-answer", id=answer.question.id)

