from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.views import View
from eab.utils import send_email_with_html_body
from .models import*
from eab.models import*
from forum.models import*
from document.models import*
from app_auth.decorator import*
from django.db import transaction
from django.template.loader import get_template
import datetime
import pdfkit


def parametre():
    try:
        parametre=Parametre.objects.all()[0]
    except Exception as e:
        parametre=None
    
    if parametre == None :
        return redirect("maintenance")
    else:
        return parametre
    
def userPriority():
    users=User.objects.all()
    #Memebre prioritaire
    tabUserPriority=[]
    count=0
    for user in users:
        try:
            if user.profile and user.profile.priority==1:
                if count <=2:
                    tabUserPriority.append(user)
                    count+=1
        except:
            pass
    return tabUserPriority

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
        number+=Answer.objects.filter(question_id=question.id, status=0).count()
    return number

@login_required(login_url='connection/login')
def mescours(request):
    date=datetime.datetime.now()

    cours=Cours.objects.values("discipline_id").filter(user_id=request.user.id).annotate(effectif=Count("discipline_id"))
    tabCours=[]
    for course in cours:
        dic={}
        discipline=Discipline.objects.get(id=course["discipline_id"])
        dic["discipline"]=discipline
        dic["effectif"]=course["effectif"]
        #On fait une mise à jour de statut
        list_cours=Cours.objects.filter(discipline_id=course["discipline_id"], user_id=request.user.id, st=1)
        for d in list_cours:
            d.st=2
            d.save()
        #On compte le nombre de nouvelles notifications
        countnotif=Cours.objects.filter(discipline_id=course["discipline_id"],user_id=request.user.id, st=2).count()
        dic["countnotif"]=countnotif
        tabCours.append(dic)

    context={
        "cours":tabCours,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "cours/mescours.html", context)

@login_required(login_url='connection/login')
def d_cours(request, id):
    date=datetime.datetime.now()
    discipline=Discipline.objects.get(id=id)
    cours=Cours.objects.values("composant_id").filter(discipline_id=id,user_id=request.user.id).annotate(effectif=Count("composant_id"))
    tabComposants=[]
    for course in cours:
        dic={}
        composant=Composant.objects.get(id=course["composant_id"])
        dic["composant"]=composant
        dic["effectif"]=course["effectif"]
        #On fait une mise à jour de statut
        list_cours=Cours.objects.filter(composant_id=course["composant_id"], user_id=request.user.id, st=2)
        for d in list_cours:
            d.st=3
            d.save()
        #On compte le nombre de nouvelles notifications
        countnotif=Cours.objects.filter(composant_id=course["composant_id"],user_id=request.user.id, st=3).count()
        dic["countnotif"]=countnotif
        tabComposants.append(dic)

    context={
        "discipline":discipline,
        "composants":tabComposants,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "cours/d-cours.html", context)

@login_required(login_url='connection/login')
def details_cours(request, id):
    date=datetime.datetime.now()

    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id, user_id=request.user.id)
    #On fait une mise à jour de statut
    list_cours=Cours.objects.filter(composant_id=id, user_id=request.user.id, st=3)
    for d in list_cours:
        d.st=4
        d.save()
    
    context={
        "composant":composant,
        "cours":cours,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "cours/details-cours.html", context)

@login_required(login_url='connection/login')
def add_cours(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        title=request.POST["title"]
        niveau=request.POST["niveau"]
        file=request.FILES["file"]
        comment=request.POST["comment"]
        type=request.POST["type"]
        price=0
        if type=="Payant":
            price=request.POST["price"]
        
        discipline=request.POST["discipline"]
        composant=request.POST["composant"]
        cours=Cours(date=date,file=file,comment=comment,type=type,price=price,composant_id=composant,discipline_id=discipline,user_id=request.user.id,niveau=niveau,title=title)
        cours.save()
        return redirect("cours/mescours")
    disciplines=Discipline.objects.all()
    context={
        "disciplines":disciplines,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "cours/add_cours.html", context)

@login_required(login_url='connection/login')
def edit_cours(request,id):
    date=datetime.datetime.now()

    cours=Cours.objects.get(id=id)
    if request.method=="POST":
        #file=request.POST["file"]
        title=request.POST["title"]
        niveau=request.POST["niveau"]
        comment=request.POST["comment"]
        type=request.POST["type"]
        price=request.POST["price"]
        prix=0
        if price :
            prix=price

        file=None
        if request.POST.get('file', True):
            file=request.FILES["file"]
        
        discipline=request.POST["discipline"]
        composant=request.POST["composant"]

        cours.title=title
        cours.niveau=niveau
        cours.type=type
        cours.price=prix
        if file is not None:
            cours.file=file
        cours.comment=comment
        cours.composant_id=composant
        cours.discipline_id=discipline

        cours.save()
        return redirect("cours/details-cours", id=cours.composant.id)
    
    disciplines=Discipline.objects.all()
    tabDisciplines=[]
    for discipline in disciplines:
        if discipline.id != cours.discipline.id:
            tabDisciplines.append(discipline)

    composants=Composant.objects.filter(discipline_id=cours.discipline.id)
    tabComposants=[]
    for composant in composants:
        if composant.id !=cours.composant.id:
            tabComposants.append(composant)
    context={
        "cours":cours,
        "disciplines":tabDisciplines,
        "composants":tabComposants,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "cours/edit_cours.html", context)

class getCompDiscipline(View):
    def get(self, request, id, *args, **kwargs):    
        composants=Composant.objects.filter(discipline_id=id)
        context={
            "composants":composants
        }
        return render(request, "ajaxCompDisc.html", context)
    
class getPrice(View):
    def get(self, request, id, *args, **kwargs):    
        type=id
        context={
            "type":type
        }
        return render(request, "ajaxType.html", context)


@login_required(login_url='connection/login')
def delcours(request,id):
    cours=Cours.objects.get(id=id)
    cours.delete()
    return redirect("cours/dcours", id=cours.composant.id)

def delete_cours(request,id):
    cours=Cours.objects.filter(discipline_id=id)
    for cour in cours:
        cour.delete()
    return redirect("cours/listcours", id=cours.composant.id)

def delcourscmp(request,id):
    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id)
    for cour in cours:
        cour.delete()
    return redirect("cours/detcours", id=composant.discipline_id)

#=========== Suppression des documents pour un memebre ====================
@login_required(login_url='connection/login')
def del_cours(request,id):
    cours=Cours.objects.get(id=id)
    cours.delete()
    return redirect("details_cours", id=cours.composant.id)

#Suppression des documents d'une discipline d'un membre
@login_required(login_url='connection/login')
def deldocdisiscipline(request,id):
    cours=Cours.objects.filter(discipline_id=id, user_id=request.user.id)
    for cour in cours:
        cour.delete()
    return redirect("mescours")

#Suppression des documents de composant d'un membre
@login_required(login_url='connection/login')
def deldoccomposant(request,id):
    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id, user_id=request.user.id)
    for cour in cours:
        cour.delete()
    return redirect("d-cours", id=composant.discipline_id)


def cours(request):
    date=datetime.datetime.now()

    liste_cours=Cours.objects.values("composant_id").filter(status="Cours publié").annotate(effectif=Count("composant_id")).order_by("discipline_id")
    tabComposant=[]
    for item in liste_cours:
        dic={}
        composant=Composant.objects.get(id=item["composant_id"])
        dic["id"]=item["composant_id"]
        dic["libelle"]=composant.libelle
        dic["effectif"]=item["effectif"]
        tabComposant.append(dic)

    cours=Cours.objects.filter(status="Cours publié").order_by("-date")

    paginator = Paginator(cours, 12)
    num_page=request.GET.get('page')
    cours=paginator.get_page(num_page)
    #On affiche la valeur du panier
    try:
        panier=Panier.objects.get(user_id=request.user.id)
    except Exception as e:
        panier=None
    
    count=0
    if panier == None:
        pass
    else : 
        cpanier=eval(panier.cquantite)
        for k in cpanier.items():
            count+=1
    
    context={
        "count":count,
        "composants":tabComposant,
        "cours":cours,
        "date":date,
        "userpriorities":userPriority(),
        "parametre":parametre(),
    }
    return render(request, "cours/cours.html", context)

def details(request,id):
    date=datetime.datetime.now()

    cours=Cours.objects.get(id=id)
    #On affiche la valeur du panier
    try:
        panier=Panier.objects.get(user_id=request.user.id)
    except Exception as e:
        panier=None
    
    count=0
    if panier == None:
        pass
    else : 
        cpanier=eval(panier.cquantite)
        for k in cpanier.items():
            count+=1

    context={
        "count":count,
        "course":cours,
        "date":date,
        "userpriorities":userPriority(),
        "parametre":parametre(),
    }
    return render(request, "cours/details.html", context)


class getCours(View):
    def get(self, request, id, *args, **kwargs): 

        cours=Cours.objects.filter(status="Cours publié", composant_id=id)

        paginator = Paginator(cours, 12)
        num_page=request.GET.get('page')
        cours=paginator.get_page(num_page)

        composant=Composant.objects.get(id=id)

        context={
            "composant":composant,
            "cours":cours,
            "parametre":parametre(),
        }
        return render(request, "ajaxCours.html", context)
    
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def listcours(request):
    date=datetime.datetime.now()

    cours=Cours.objects.values('discipline_id').annotate(effectif=Count("discipline_id"))
    tabCours=[]
    for item in cours:
        discipline=Discipline.objects.get(id=item["discipline_id"])
        dic={}
        dic["id"]=item["discipline_id"]
        dic["discipline"]=discipline.libelle
        dic["effectif"]=item["effectif"]
        tabCours.append(dic)

    context={
            "cours":tabCours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/listcours.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def detcours(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)
    cours=Cours.objects.values('composant_id').filter(discipline_id=id).annotate(effectif=Count("composant_id"))
    tabCours=[]

    for item in cours:
        composant=Composant.objects.get(id=item["composant_id"])
        dic={}
        dic["id"]=item["composant_id"]
        dic["composant"]=composant.libelle
        dic["effectif"]=item["effectif"]
        tabCours.append(dic)

    context={
            "discipline":discipline,
            "cours":tabCours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/detcours.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def dcours(request,id):
    date=datetime.datetime.now()

    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id).order_by("-id")

    context={
            "composant":composant,
            "cours":cours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/dcours.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def viewcours(request,id):
    date=datetime.datetime.now()

    cours=Cours.objects.get(id=id)

    if request.method=="POST":
        status=request.POST["status"]
        content=request.POST["content"]

        cours.status=status
        cours.content=content
        cours.st=1
        cours.save()
        return redirect("cours/v-cours",id=id)

    context={
            "cours":cours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }

    return render(request, "cours/v-cours.html", context)

# On determine les cours publiés
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def courspub(request):
    date=datetime.datetime.now()

    dataDiscipline=[]
    disciplines=Cours.objects.values("discipline_id").filter(status="Cours publié").annotate(effectif=Count("discipline_id"))
    for data in disciplines:
        dic={}
        discipline=Discipline.objects.get(id=data["discipline_id"])
        dic["id"]=data["discipline_id"]
        dic["libelle"]=discipline.libelle
        dic["effectif"]=data["effectif"]
        dataDiscipline.append(dic)

    context={
            "disciplines":dataDiscipline,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/courspub.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def detcourspub(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)

    dataComposant=[]
    composants=Cours.objects.values("composant_id").filter(discipline_id=id, status="Cours publié").annotate(effectif=Count("composant_id"))
    for data in composants:
        dic={}
        composant=Composant.objects.get(id=data["composant_id"])
        dic["id"]=data["composant_id"]
        dic["libelle"]=composant.libelle
        dic["effectif"]=data["effectif"]
        dataComposant.append(dic)

    context={
            "discipline":discipline,
            "composants":dataComposant,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/detcourspub.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def dcourspub(request,id):
    date=datetime.datetime.now()

    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id, status="Cours publié").order_by("-id")
    context={
            "composant":composant,
            "cours":cours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/dcourspub.html", context)


# On determine les cours publiés
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def coursencours(request):
    date=datetime.datetime.now()

    dataDiscipline=[]
    disciplines=Cours.objects.values("discipline_id").filter(status="Traitement en cours").annotate(effectif=Count("discipline_id"))
    for data in disciplines:
        dic={}
        discipline=Discipline.objects.get(id=data["discipline_id"])
        dic["id"]=data["discipline_id"]
        dic["libelle"]=discipline.libelle
        dic["effectif"]=data["effectif"]
        dataDiscipline.append(dic)

    context={
            "disciplines":dataDiscipline,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/c-encours.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def detcoursencours(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)

    dataComposant=[]
    composants=Cours.objects.values("composant_id").filter(discipline_id=id, status="Traitement en cours").annotate(effectif=Count("composant_id"))
    for data in composants:
        dic={}
        composant=Composant.objects.get(id=data["composant_id"])
        dic["id"]=data["composant_id"]
        dic["libelle"]=composant.libelle
        dic["effectif"]=data["effectif"]
        dataComposant.append(dic)

    context={
            "discipline":discipline,
            "composants":dataComposant,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/detcoursencours.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def dcoursencours(request,id):
    date=datetime.datetime.now()
    
    if request.method=="POST":
        id=request.POST["id"]
        status=request.POST["status"]
        content=request.POST["content"]

        etat=0
        if status == "Traitement en cours" and status == "Cours non retenu":
            etat=0
        else:
            etat+=1

        cours=Cours.objects.get(id=id)
        
        cours.etat=etat
        cours.status=status
        cours.content=content
        cours.st=1
        cours.save()
        return redirect("cours/dcoursencours",id=id)
    else:
        composant=Composant.objects.get(id=id)
        listcours=Cours.objects.filter(composant_id=id, status="Traitement en cours").order_by("-id")
        context={
                "composant":composant,
                "cours":listcours,
                "date":date,
                "parametre":parametre(),
                "countanswer":nbnew_answer(request),
                "count":nbnew_message(request),
                "users":new_message(request),
        }
        return render(request, "cours/dcoursencours.html", context)

############################## Cours non publiés ####################################
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def coursnonpub(request):
    date=datetime.datetime.now()

    dataDiscipline=[]
    disciplines=Cours.objects.values("discipline_id").filter(status="Cours non retenu").annotate(effectif=Count("discipline_id"))
    for data in disciplines:
        dic={}
        discipline=Discipline.objects.get(id=data["discipline_id"])
        dic["id"]=data["discipline_id"]
        dic["libelle"]=discipline.libelle
        dic["effectif"]=data["effectif"]
        dataDiscipline.append(dic)

    context={
            "disciplines":dataDiscipline,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/coursnonpub.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def detcoursnonpub(request,id):
    date=datetime.datetime.now()

    discipline=Discipline.objects.get(id=id)

    dataComposant=[]
    composants=Cours.objects.values("composant_id").filter(discipline_id=id, status="Cours non retenu").annotate(effectif=Count("composant_id"))
    for data in composants:
        dic={}
        composant=Composant.objects.get(id=data["composant_id"])
        dic["id"]=data["composant_id"]
        dic["libelle"]=composant.libelle
        dic["effectif"]=data["effectif"]
        dataComposant.append(dic)

    context={
            "discipline":discipline,
            "composants":dataComposant,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/detcoursnonpub.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def dcoursnonpub(request,id):
    date=datetime.datetime.now()

    composant=Composant.objects.get(id=id)
    cours=Cours.objects.filter(composant_id=id, status="Cours non retenu").order_by("-id")
    context={
            "composant":composant,
            "cours":cours,
            "date":date,
            "parametre":parametre(),
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
    }
    return render(request, "cours/dcoursnonpub.html", context)

#============================ Panier =======================================
class addPanier(View):
    def get(self, request, id, *args, **kwargs):   
        try:
            panier=Panier.objects.get(user_id=request.user.id)
        except Exception as e:
            panier=None
        
        if panier == None:
            cours=Cours.objects.get(id=id)
            dic={}
            tabCours=[]
            tabCours.append(1)
            tabCours.append(cours.discipline.libelle)
            tabCours.append(cours.composant.libelle)
            tabCours.append(cours.title)
            tabCours.append(cours.comment)
            tabCours.append(cours.price)
            
            dic[id]=tabCours
            
            panier=Panier(user_id=request.user.id, cquantite=dic)
            panier.save()

            p=Panier.objects.get(user_id=request.user.id)
            cpanier=eval(p.cquantite)

            count=0
            for k in cpanier.items():
                count+=1
            
            context={
                "quantite":count
            }
            return render(request, "addPanier.html", context)
        else:
            cpanier=eval(panier.cquantite)
            tabkey=[]
            for k in cpanier.items():
                tabkey.append(k)
            
            if id in tabkey:
                count=0
                for k in cpanier.items():
                    count+=1
                #quantite=len(cpanier.keys())
                context={
                    "quantite":count
                }
                return render(request, "addPanier.html", context)
            else:
                cours=Cours.objects.get(id=id)

                tabCours=[]
                tabCours.append(1)
                tabCours.append(cours.discipline.libelle)
                tabCours.append(cours.composant.libelle)
                tabCours.append(cours.title)
                tabCours.append(cours.comment)
                tabCours.append(cours.price)
                
                cpanier[id]=tabCours

                panier.cquantite=cpanier
                panier.save()

                p=Panier.objects.get(user_id=request.user.id)
                cpanier=eval(p.cquantite)

                count=0
                for k in cpanier.items():
                    count+=1
                #quantite=len(cpanier.keys())
                context={
                    "quantite":count
                }
                return render(request, "addPanier.html", context)
        
def panier(request):
    try:
        panier=Panier.objects.get(user_id=request.user.id)
    except Exception as e:
        panier=None
    
    if panier == None:
        return redirect("cours")
    
    cquantite=eval(panier.cquantite)

    prixtotal=0
    quantitetotale=0
    tabPanier=[]
    for k,v in cquantite.items():
        dic={}
        dic["id"]=k
        dic["quantite"]=v[0]
        dic["discipline"]=v[1]
        dic["composant"]=v[2]
        dic["title"]=v[3]
        dic["comment"]=v[4]
        dic["price"]=v[5]
        tabPanier.append(dic)

        prixtotal+=v[5]
        quantitetotale+=v[0]
    
    count=0
    cpanier=eval(panier.cquantite)
    for k in cpanier.items():
        count+=1

    context={
            "count":count,
            "quantitetotale":quantitetotale,
            "prixtotal":prixtotal,
            "paniers":tabPanier,
            "userpriorities":userPriority(),
            "parametre":parametre()
    }
    return render(request, "commande/panier.html", context)

@login_required(login_url='connection/login')
def del_panier(request, id):

    panier=Panier.objects.get(user_id=request.user.id)
    cquantite=eval(panier.cquantite)
    
    del cquantite[id]

    panier.cquantite=cquantite
    panier.save()
    return redirect("commande/panier")

@login_required(login_url='connection/login')
def paiement(request):
    try:
        panier=Panier.objects.get(user_id=request.user.id)
    except Exception as e:
        panier=None
    
    if panier == None:
        return redirect("cours/cours")
    cquantite=eval(panier.cquantite)
    #On calcule le prix total d'achat
    prixtotal=0
    for k,v in cquantite.items():
        prixtotal+=v[5]

    context={
            "prixtotal":prixtotal,
            "userpriorities":userPriority(),
            "parametre":parametre()
    }

    return render(request, "commande/paiement.html", context)

@login_required(login_url='connection/login')
@transaction.atomic
def validecmd(request):
    #On affiche la valeur du panier
    try:
        panier=Panier.objects.get(user_id=request.user.id)
    except Exception as e:
        panier=None
    
    if panier == None:
        return redirect("cours/cours")
    else:
        cquantite=eval(panier.cquantite)

    prixtotal=0
    for k,v in cquantite.items():
        prixtotal+=v[5]

    commande=Commande(total=prixtotal, user_id=request.user.id, ucours=cquantite)
    commande.save()
    #On supprime le contenu du panier
    panier.delete()  
    return redirect("commande/success")

@login_required(login_url='connection/login')
@transaction.atomic
def success(request):
    date=datetime.datetime.now()
    #On recupère des documents
    tabCours=[]
    commande=Commande.objects.filter(user_id=request.user.id).order_by("-id")[0]
    doc=eval(commande.ucours)
    for k,v in doc.items():
        cours=Cours.objects.get(id=k)
        tabCours.append(cours)
    
    subject="Documents"
    template="email/emaildocument.html"
    receivers = [request.user.email]
    #On recupère le membre qui a effectué l'achat
    user=User.objects.get(id=request.user.id)            
    ctxt = {
        "user":user,
        "count":len(tabCours),
        "cours":tabCours,
        'date': date,
        'parametre': parametre()
    }

    has_send = send_email_with_html_body(
        subjet=subject,
        receivers=receivers,
        template=template,
        context=ctxt
    )
    
    context={
        "commande":commande,
        "cours":tabCours,
        "userpriorities":userPriority(),
        "parametre":parametre()
    }
    return render(request, "commande/success.html", context)

@login_required(login_url='connection/login')
def echec(request):
    parametre=Parametre.objects.all()[0]
    context={
        "parametre":parametre
    }
    return render(request, "commande/echec.html", context)

@login_required(login_url='connection/login')
def commandes(request):
    date=datetime.datetime.now()
    commandes=Commande.objects.filter(status=0).order_by("-id")

    for commande in commandes:
        commande.status=1
        commande.save()
 
    commandes=Commande.objects.filter(status=1).order_by("-id")
    context={
        "commandes":commandes,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "commande/commandes.html", context)

@login_required(login_url='connection/login')
def delachat(request, id):
    achat=Commande.objects.get(id=id)
    achat.delete()
    return redirect("commande/commandes")

@login_required(login_url='connection/login')
def detachat(request, id):
    date=datetime.datetime.now()
    commande=Commande.objects.get(id=id)
    panier=eval(commande.ucours)
    prixtotal=0
    quantitetotal=0
    tabAchat=[]
    for k,v in panier.items():
        dic={}
        dic["id"]=k
        dic["quantite"]=v[0]
        dic["discipline"]=v[1]
        dic["composant"]=v[2]
        dic["title"]=v[3]
        dic["comment"]=v[4]
        dic["price"]=v[5]
        tabAchat.append(dic)

        quantitetotal+=v[0]
        prixtotal+=v[5]

    context={
        "commande":commande,
        "achats":tabAchat,
        "total":prixtotal,
        "qtetotal":quantitetotal,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "commande/detachat.html", context)

@login_required(login_url='connection/login')
def doc_purchased(request):
    date=datetime.datetime.now()
    commandes=Commande.objects.filter(user_id=request.user.id)
    tabAchats=[]
    for commande in commandes:
        doc=eval(commande.ucours)
        dic={}
        dic["id"]=commande.id
        dic["total"]=commande.total
        dic["datecommande"]=commande.datecommande
        tabcours=[]
        for k,c in doc.items():
            cours=Cours.objects.get(id=k)
            dict={}
            dict["qte"]=c[0]
            dict["discipline"]=c[1]
            dict["composant"]=c[2]
            dict["title"]=c[3]
            dict["comment"]=c[4]
            dict["price"]=c[5]
            dict["file"]=cours.file

            tabcours.append(dict)
        dic["cours"]=tabcours
        tabAchats.append(dic)
    context={
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "achats":tabAchats
    }
    return render(request, "commande/doc-pur.html", context)

@login_required(login_url='connection/login')
def my_doc_purchased(request):
    date=datetime.datetime.now()
    tabAchats=[]
    #On recupère tous les documents du mmenbre
    cours=Cours.objects.filter(user_id=request.user.id)

    for c in cours:
        #On recupère tous les achats
        commandes=Commande.objects.filter(statusachat=0)
        for commande in commandes:
            doc=eval(commande.ucours)
            for k,v in doc.items():
                #On selectionne uniquement les documents du membre qui ont été acheté 
                if k==c.id:
                    #Changement de status
                    commande.statusachat=1
                    commande.save()

    for c in cours:
        #On recupère tous les achats
        commandes=Commande.objects.filter()
        dic={}
        tab=[]
        count=0
        for commande in commandes:
            doc=eval(commande.ucours)
            for k,v in doc.items():
                #On selectionne uniquement les documents du membre qui ont été acheté 
                if k==c.id:
                    count+=1
                    dict={}
                    dict["id"]=commande.id
                    dict["date"]=commande.datecommande
                    dict["qte"]=v[0]
                    dict["discipline"]=v[1]
                    dict["composant"]=v[2]
                    dict["title"]=v[3]
                    dict["comment"]=v[4]
                    dict["price"]=v[5]
                    dict["file"]=c.file
                    tab.append(dict)
            #tab.append(count)
            if len(tab)>0:
                dic[c.id]=tab
        if len(dic.keys())>0:
            tabAchats.append(dic)
    context={
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "achats":tabAchats
    }
    return render(request, "commande/my-docpur.html", context)

class fetchdoc(View):
    def get(self, request, id, *args, **kwargs):
        #On compte le nombre de cours
        countcoursencours=Cours.objects.filter(discipline_id=id,status="Traitement en cours").count()
        countcourspublie=Cours.objects.filter(discipline_id=id,status="Cours publié").count()
        countcoursnonpublie=Cours.objects.filter(discipline_id=id,status="Cours non retenu").count()
        total=Cours.objects.filter(discipline_id=id).count()
        discipline=Discipline.objects.get(id=id)
        context={
            "discipline":discipline,
            "total":total,
            "countcoursencours":countcoursencours,
            "countcourspublie":countcourspublie,
            "countcoursnonpublie":countcoursnonpublie
        }
        return render(request, "fetchdoc.html", context)
    
class fetchdoccmp(View):
    def get(self, request, id, *args, **kwargs):

        #On compte le nombre de cours
        countcoursencours=Cours.objects.filter(composant_id=id,status="Traitement en cours").count()
        countcourspublie=Cours.objects.filter(composant_id=id,status="Cours publié").count()
        countcoursnonpublie=Cours.objects.filter(composant_id=id,status="Cours non retenu").count()
        total=Cours.objects.filter(composant_id=id).count()
        composant=Composant.objects.get(id=id)
        context={
            "composant":composant,
            "total":total,
            "countcoursencours":countcoursencours,
            "countcourspublie":countcourspublie,
            "countcoursnonpublie":countcoursnonpublie
        }
        return render(request, "fetchdoccmp.html", context)

@login_required(login_url='connection/login')
def facture(request,id):
    commande=Commande.objects.get(id=id)
    panier=eval(commande.ucours)
    prixtotal=0
    quantitetotal=0
    tabAchat=[]
    for k,v in panier.items():
        dic={}
        dic["id"]=k
        dic["quantite"]=v[0]
        dic["discipline"]=v[1]
        dic["composant"]=v[2]
        dic["title"]=v[3]
        dic["comment"]=v[4]
        dic["price"]=v[5]
        tabAchat.append(dic)

        quantitetotal+=v[0]
        prixtotal+=v[5]

    context={
        "commande":commande,
        "achats":tabAchat,
        "total":prixtotal,
        "qtetotal":quantitetotal,
        "parametre":parametre()
    }
    template=get_template("commande/facture.html")
    html=template.render(context)
    options={
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }

    pdf=pdfkit.from_string(html, False, options)
    reponse = HttpResponse(pdf, content_type='application/pdf')
    reponse['Content-Disposition']="attachement"
    return reponse

        
