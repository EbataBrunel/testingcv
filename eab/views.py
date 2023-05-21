from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Count
from django.views import View
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from xhtml2pdf import pisa
from .models import*
from .forms import*
from .utils import send_email_with_html_body
from forum.models import*
from document.models import*
from annonce.models import*
from app_auth.decorator import*
import datetime
import re
import pdfkit

def generatecv2(request):
    template_path = 'cv/test.html'

    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=request.user.id).order_by("-annee_id")
    #======== Competence ==============
    competenceLangages=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1)
    cpLangage=False
    if competenceLangages.count() > 0:
        cpLangage=True

    competenceFrameworks=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1)
    cpFramework=False
    if competenceFrameworks.count() > 0:
        cpFramework=True

    competenceSystemes=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1)
    cpSysteme=False
    if competenceSystemes.count() > 0:
        cpSysteme=True

    competenceSE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1)
    cpSystemeE=False
    if competenceSE.count() > 0:
        cpSystemeE=True

    competenceLogiciels=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1)
    cpLogiciel=False
    if competenceLogiciels.count() > 0:
        cpLogiciel=True

    competenceModelisations=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1)
    cpModelisation=False
    if competenceModelisations.count() > 0:
        cpModelisation=True

    competenceOE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1)
    cpOutilsE=False
    if competenceOE.count() > 0:
        cpOutilsE=True

    competenceBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1)
    cpBureautique=False
    if competenceBureautique.count() > 0:
        cpBureautique=True

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=False
    if competenceLangues.count() > 0:
        cpLangue=True

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=False
    if competenceLoisirs.count() > 0:
        cpLoisir=True

    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=request.user.id, status=1)
    user=User.objects.get(id=request.user.id)
    context={
        "user":user,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competenceLangages":competenceLangages,
        "cpLangage":cpLangage,
        "competenceFrameworks":competenceFrameworks,
        "cpFramework":cpFramework,
        "competenceSystemes":competenceSystemes,
        "cpSysteme":cpSysteme,
        "competenceSE":competenceSE,
        "cpSystemeE":cpSystemeE,
        "competenceLogiciels":competenceLogiciels,
        "cpLogiciel":cpLogiciel,
        "competenceModelisations":competenceModelisations,
        "cpModelisation":cpModelisation,
        "competenceOE":competenceOE,
        "cpOutilsE":cpOutilsE,
        "competenceBureautique":competenceBureautique,
        "cpBureautique":cpBureautique
    }

    context2 = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

## https://www.youtube.com/watch?v=Bfgtp62VFeU

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
        if int(diccode["user1"])==request.user.id:
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

def home(request):

    if request.method=="POST":
        name=request.POST["name"]
        users=User.objects.filter(last_name__icontains=name)
        tabUsers=[]
        if len(users) > 0:
            for user in users:
                try:
                    if user.profile and user.profile.status==1:
                        tabUsers.append(user)
                except:
                    pass
        else:
            list_users=User.objects.filter(first_name__icontains=name)
            for user in list_users:
                try:
                    if user.profile and user.profile.status==1:
                        tabUsers.append(user)
                except:
                    pass

        paginator = Paginator(tabUsers, 10)
        num_page=request.GET.get('page')
        try:
            tabUsers=paginator.get_page(num_page)
        except PageNotAnInteger:
            tabUsers=paginator.get_page(1)
        except EmptyPage:
            tabUsers=paginator.get_page(paginator.num_page)

        context={
            "users":tabUsers,
            "userpriorities":userPriority(),
            "parametre":parametre,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "newusers":new_message(request)
        }
        return render(request, "index.html",context)
    
    tabUsers=[]
    users=User.objects.all()
    for user in users:
        try:
            if user.profile and user.profile.status==1:
                tabUsers.append(user)
        except Exception as e:
            pass

    paginator = Paginator(tabUsers, 10)
    num_page=request.GET.get('page')
    tabUsers=paginator.get_page(num_page)
    
    context={
        "users":tabUsers,
        "userpriorities":userPriority(),
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "newusers":new_message(request)
    }
    return render(request, "index.html",context)

def authorization(request):
    date=datetime.datetime.now()
    context={
        "parametre":parametre(),
        "date":date
    }
    return render(request, "authorization.html", context)

@login_required(login_url='connection/login')
def dashboard(request):
    nombre_users=0
    nombre_customers=0
    nombre_contacts=Contact.objects.filter(statut=0,status=0).count()

    users=User.objects.all()
    for user in users:
        try:
            if user.groups.exists():
                group=user.groups.all()[0].name
                if group=="customer":
                    nombre_customers+=1
                if group=="admin":
                    nombre_users+=1
        except Exception as e:
            pass

    #On compte le nombre de cours
    countcoursencours=Cours.objects.filter(status="Traitement en cours").count()
    countcourspublie=Cours.objects.filter(status="Cours publié").count()
    countcoursnonpublie=Cours.objects.filter(status="Cours non retenu").count()

    countcourstotal=countcoursencours + countcourspublie +  countcoursnonpublie

    #On compte le nombre de nouveaux achats
    countachats=Commande.objects.filter(status=0).count()
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

    #On compte le nombre toutes les questions qui ont été posé après la dernière connexion du membre
    questions=Question.objects.filter(date__gt=request.user.last_login)
    countquestion=0
    for question in questions:
        if question.user_id != request.user.id:
            countquestion+=1

    #On compte le nombre de nouvelles notifications
    countnotif=Cours.objects.filter(user_id=request.user.id,st=1).count()
    #On compte le nombre de commande
    countcommande=Commande.objects.filter(user_id=request.user.id).count()
    #On recupère tous les documents du mmenbre
    countachat=0
    cours=Cours.objects.filter(user_id=request.user.id)
    for c in cours:
        #On selectionne les achats de chaque document
        commandes=Commande.objects.filter(statusachat=0)
        for commande in commandes:
            doc=eval(commande.ucours)
            for k,v in doc.items():
                #On selectionne uniquement les documents du membre qui ont été acheté 
                if k==c.id:
                    countachat+=1

    annonces=Annonce.objects.all()
    #On recupère la dernière annonce
    annonce=annonces[len(annonces)-1]
    date=datetime.datetime.now()
    context={
        "annonce":annonce,
        "userspriorities":tabUserPriority,
        "countachat":countachat,
        "countachats":countachats,
        "countnotif":countnotif,
        "countcoursencours":countcoursencours,
        "countcourspublie":countcourspublie,
        "countcoursnonpublie":countcoursnonpublie,
        "countcourstotal":countcourstotal,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date,
        "countusers":nombre_users,
        "countcustomers":nombre_customers,
        "nombre_contact":nombre_contacts,
        "countquestion":countquestion,
        "countcommande":countcommande
    }
    return render(request, "dashboard.html",context)

#================== Fonctions d'erreurs ====================
def handler404(request, exception):
    context={}
    return render(request, "400.html", context)

def handler500(request):
    context={}
    return render(request, "500.html", context)

def maintenance(request):
    context={}
    return render(request, "maintenance.html", context)

#=================== Gestion de l'année ======================
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def annees(request):
    date=datetime.datetime.now()

    annees=Annee.objects.all()
    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "annees":annees,
        "parametre":parametre(),
        "date":date
    }
    return render(request, "annee/annees.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def add_annee(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        libelle=request.POST["libelle"]
        query=Annee.objects.filter(libelle=libelle)
        if query.exists():
            return JsonResponse({"status":0}) 
        else:
            annee=Annee(libelle=libelle)
            count0=Annee.objects.all().count()
            annee.save()
            count1=Annee.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
               return JsonResponse({'status':1}) 
    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "annee/add_annee.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def edit_annee(request,id):
    date=datetime.datetime.now()
    annee=Annee.objects.get(id=id)
    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "annee":annee,
        "parametre":parametre(),
        "date":date
    }
    return render(request, "annee/edit_annee.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def edit_an(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            annee=Annee.objects.get(id=id)
        except:
            annee=None

        if annee == None:
            return JsonResponse({'status':1})
        else: 
            libelle=request.POST["libelle"]
            #On verifie si cette année a déjà été enregistrée
            annees=Annee.objects.exclude(id=id)
            tabAnnee=[]
            for an in annees:          
                tabAnnee.append(an.libelle)
            #On verifie si cette année existe déjà
            if libelle in tabAnnee:
                    return JsonResponse({"status":0}) 
            else:
                annee.libelle=libelle
                annee.save()
                return JsonResponse({'status':'Save'})


@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def del_annee(request,id):
    annee=Annee.objects.get(id=id)
    annee.delete()
    return redirect("annee/annees")

#=================== Gestion de contact ======================
@transaction.atomic
@csrf_exempt
def contact(request):
    if request.method=="POST":    
        date=datetime.datetime.now()    
        form=ContactForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            email=form.cleaned_data["email"]
            subject=form.cleaned_data["subject"]
            message=form.cleaned_data["message"]
            #On verifie si l'adresse e-mail correspond bien
            regexp = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$"
            if not re.search(regexp, email):
                return JsonResponse({'status':0})
            else:
                contact=Contact(name=name, email=email, subject=subject, message=message, statut=0, codes=None,status=False)
                count0=Contact.objects.all().count()
                contact.save()
                count1=Contact.objects.all().count()

                subject="Confirmation"
                template="email/emailcontact.html"
                receivers = [email]
                
                context = {
                    'email':email,
                    'date': date,
                    'parametre': parametre()
                }
                has_send = send_email_with_html_body(
                    subjet=subject,
                    receivers=receivers,
                    template=template,
                    context=context
                )
                #On verifie si le message a bien été envoyé
                if count0 < count1 and has_send == True:
                    return JsonResponse({'status':'Save'})
                else:
                    return JsonResponse({'status':1})
        else:
            form=ContactForm()

    form=ContactForm()
    date=datetime.datetime.now()
    context={
        "form":form,
        "parametre":parametre(),
        "userpriorities":userPriority(),
        "date":date
    }
    return render(request, "contact/contact.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def contacts(request):
    liste_contacts=Contact.objects.filter(statut=0,status=0)
    for stat in liste_contacts:
        status=stat
        status.statut=1
        status.save()

    cont=Contact.objects.values("email").filter(statut=1,status=0).annotate(effectif=Count("email"))
    tabContacts=[]
    for contact in cont:

        tab={}
        #On recupère le dernier message de chaque e-mail
        c=Contact.objects.filter(email=contact["email"], status=0).order_by("-id")[:1]
        con=c[0]
        tab["id"]=con.id
        tab["email"]=con.email
        tab["name"]=con.name
        tab["datecontact"]=con.datecontact
        tab["message"]=con.message
        tab["effectif"]=contact["effectif"]

        tabContacts.append(tab)

    tabemail=[]
    for contact in cont:
        tabemail.append(contact["email"])

    tabContacts2=[]
    cont1=Contact.objects.values("email").filter(status=0).annotate(effectif=Count("email"))
    for contact1 in cont1:
            if contact1["email"] not in tabemail :
                
                tab1={}
                c1=Contact.objects.filter(email=contact1["email"], status=0).order_by("-id")[:1]
                #On recupère le contact vue que le résultat est un tableau
                con1=c1[0]
                tab1["id"]=con1.id
                tab1["email"]=con1.email
                tab1["name"]=con1.name
                tab1["datecontact"]=con1.datecontact
                tab1["message"]=con1.message
                tab1["effectif"]=contact1["effectif"]

                tabContacts2.append(tab1)

    date=datetime.datetime.now()

    context={
        "listeContact":tabContacts, 
        "listeContact2":tabContacts2,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
        }
    return render(request, "contact/contacts.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def details_contact(request, id):
    contacts=Contact.objects.filter(email=id, status=0)
    #Changement de statut
    for stat in contacts:
        status=stat
        status.statut=2
        status.save()

    listeContact=[]
    for contact in contacts:
        dic={}
        dic["id"]=contact.id
        dic["name"]=contact.name
        dic["subject"]=contact.subject
        dic["message"]=contact.message
        dic["datecontact"]=contact.datecontact
        listeContact.append(dic)

    date=datetime.datetime.now()

    context={
        "listeContact":listeContact,
        "email":id,
        "parametre":parametre(),
        "date":date,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "contact/details_contact.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def del_contact(request, id):
    contact=Contact.objects.get(id=id)
    contact.delete()
    #On verifie s'il existe encore des contacts de cette adresse
    try:
        c=Contact.objects.filter(id=id).count()
    except Exception as e:
        return redirect("contact/contacts")

    return redirect("contact/details_contact", id=contact.email)

@login_required(login_url='connection/login')
def del_message(request, id):
    contact=Contact.objects.get(id=id)
    diccod=eval(contact.codes)
    #On verifie si le membre connecté est l'emetteur 
    if diccod["user2"] == request.user.id:
        #On verifie si le recepteur à supprimer ou pas le message de son côté.
        if contact.statutdel == 2:
            #On supprime deffinitivement le message
            contact.delete()
            return redirect("contact/detmes", id=diccod["user1"])
        else:
            #On fait une misse à jour le message
            contact.statutdel=1
            contact.save()
            return redirect("contact/detmes", id=diccod["user1"])
    else:
        #On verifie si l'emetteur à supprimer ou pas le message de son côté.
        if contact.statutdel == 1:
             #On supprime deffinitivement le message
            contact.delete()
            return redirect("contact/detmes", id=diccod["user2"])
        else:
            #On fait une misse à jour le message
            contact.statutdel=2
            contact.save()
            return redirect("contact/detmes", id=diccod["user2"])

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def delete_contact(request, id):
    cont=Contact.objects.get(id=id)
    contacts=Contact.objects.filter(email=cont.email)
    for contact in contacts:
        contact.delete()
    return redirect("contacts")

def contactuser(request,id):
    date=datetime.datetime.now()
    user=User.objects.get(id=id)
    context={
            "user":user,
            "parametre":parametre(),
            "date":date,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request)
    }
    return render(request, "contact/contactuser.html", context)


@login_required(login_url='connection/login')
def contuser(request):
    if request.method=="POST":
        id=request.POST["user"]
        subject=request.POST["subject"]
        content=request.POST["content"]
        dic={}
        #Identdifier du recepteur
        dic["user1"]=int(id)
        #Identifiant du l'emeteur
        dic["user2"]=request.user.id

        contact=Contact(
            name="",
            email="",
            subject=subject,
            statut=0,
            status=1,
            message=content,
            codes=dic
        )
        count0=Contact.objects.all().count()
        contact.save()
        count1=Contact.objects.all().count()
        if count0 < count1:
            return JsonResponse({'status':"Save"})
        else:
            return JsonResponse({'status':1})

def services(request):

    context={
        "userpriorities":userPriority(),
        "parametre":parametre()
    }
    return render(request, "contact/services.html", context)

def apropos(request):
    context={
        "userpriorities":userPriority(),
        "parametre":parametre()
    }
    return render(request, "contact/apropos.html", context)

@login_required(login_url='connection/login')
def messag(request):
    date=datetime.datetime.now()

    liste_contacts=Contact.objects.filter(statut=0, status=1)
    for contact in liste_contacts:
        diccode=eval(contact.codes)
        #On verifie si le membre connecté est le recepteur 
        if diccode["user1"]==request.user.id:
            cont=contact
            cont.statut=1
            cont.save()

    contacts=Contact.objects.filter(status=1).order_by("-id")
    tabMessage=[]
    tabIdUser=[]
    for contact in contacts:
        
        if contact.statut==1:
            diccod=eval(contact.codes)
            #On verifie si le membre connecté est le recepteur 
            if diccod["user1"]==request.user.id:
                #On verifie si ce message a été supprimé ou pas
                if contact.statutdel == 0 or contact.statutdel == 1:
                    dic={}
                    try:
                        user=User.objects.get(id=diccod["user2"])
                    except:
                        user=None
                    
                    if user is not None:
                        dic["id"]=user.id
                        dic["user"]=user
                        dic["message"]=contact.message
                        dic["datecontact"]=contact.datecontact
                        dic["statut"]=contact.statut
                        dic["status"]=1
                        tabIdUser.append(user.id)
                        tabMessage.append(dic)

            #On verifie si le membre connecté est l'emeteur   
            if diccod["user2"]==request.user.id:
                if contact.statutdel == 0 or contact.statutdel == 2:
                    dic={}
                    try:
                        user=User.objects.get(id=diccod["user1"])
                    except:
                        user=None
                    
                    if user is not None:
                        dic["id"]=user.id
                        dic["user"]=user
                        dic["message"]=contact.message
                        dic["datecontact"]=contact.datecontact
                        dic["statut"]=contact.statut
                        # on marque ou pas le nouveau message
                        dic["status"]=0
                        tabIdUser.append(user.id)    
                        tabMessage.append(dic)

        #On verifie si le membre connecté est l'emeteur  
        if contact.statut==0: 
            diccod=eval(contact.codes)
            if diccod["user2"]==request.user.id:
                if contact.statutdel == 0 or contact.statutdel == 2:
                    dic={}
                    try:
                        user=User.objects.get(id=diccod["user1"])
                    except:
                        user=None
                    
                    if user is not None:
                        dic["id"]=user.id
                        dic["user"]=user
                        dic["message"]=contact.message
                        dic["datecontact"]=contact.datecontact
                        dic["statut"]=contact.statut
                        # on marque ou pas le nouveau message
                        dic["status"]=0
                        tabIdUser.append(user.id)    
                        tabMessage.append(dic)
                
    #On supprime l'identifiant des membres qui se reproduisent
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
    for i,v in dic.items():
        for cont in tabMessage:
            if cont["id"]==i:
                if i not in tabs:
                    tabMessages.append(cont)
                    cont["nombre"]=v
                    tabs.append(i)


    #On garde un seul affichage d'un membre
    liste_contacts=Contact.objects.filter(statut=2, status=1).order_by("-id")
    tabMessage2=[]
    tabIdUser2=[]
    for contact in liste_contacts:
        diccode=eval(contact.codes)

        
        #On verifie si le membre connecté est le recepteur 
        if diccode["user1"]==request.user.id:
            if contact.statutdel == 0 or contact.statutdel == 1:
                dic={}
                try:
                    user=User.objects.get(id=diccode["user2"])
                except:
                    user=None

                if user is not None:
                    dic["id"]=user.id
                    dic["user"]=user
                    dic["message"]=contact.message
                    dic["datecontact"]=contact.datecontact
                    dic["statut"]=contact.statut
                    # on marque ou pas le nouveau message
                    dic["status"]=1
                    tabIdUser2.append(user.id)
                    tabMessage2.append(dic)

        #On verifie si le membre connecté est l'emeteur   
        if diccode["user2"]==request.user.id:
            if contact.statutdel == 0 or contact.statutdel == 2:
                dic={}
                try:
                    user=User.objects.get(id=diccode["user1"])
                except:
                    user=None

                if user is not None:
                    dic["id"]=user.id
                    dic["user"]=user
                    dic["message"]=contact.message
                    dic["datecontact"]=contact.datecontact
                    dic["statut"]=contact.statut
                    # on marque ou pas le nouveau message
                    dic["status"]=0
                    tabIdUser2.append(user.id)    
                    tabMessage2.append(dic)

    #On supprime l'identifiant des membres qui se reproduisent
    tab2=[]
    for i in tabIdUser2:
        if i not in tab2:
            tab2.append(i)

    #On affiche une seule fois le nom de l'emeteur
    tb=[]
    for mes in tabMessages:
        tb.append(mes["id"])
    tab0=[]
    for k in tab2:
        if k not in tb:
           tab0.append(k) 

    tabMessages2=[]
    tabs2=[]
    for i in tab0:
        for cont in tabMessage2:
            if cont["id"]==i:
                if i not in tabs2:
                    tabMessages2.append(cont)
                    tabs2.append(i)

    #On trie les messages par ordre d'arrivé
    """tabMessageOrdonnee=[] 
    for message in tabMessages:
        tabMessageOrdonnee.append(message)

    for message in tabMessages2:
        tabMessageOrdonnee.append(message)"""

    context={
        "contacts":tabMessages,
        "contacts2":tabMessages2,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "contact/messages.html", context)

#Détails des messages 
@login_required(login_url='connection/login')
def detmes(request,id):
    date=datetime.datetime.now()
    user=User.objects.get(id=id)

    contacts=Contact.objects.filter(statut=0, status=1)
    for contact in contacts:
        diccode=eval(contact.codes)
        #On verifie si le membre connecté est le recepteur 
        if diccode["user1"]==request.user.id:
            cont=contact
            cont.statut=2
            cont.save()

    list_contacts=Contact.objects.filter(statut=1, status=1)
    for contact in list_contacts:
        diccode=eval(contact.codes)
        #On verifie également si le membre connecté est le recepteur 
        if diccode["user1"]==request.user.id:
            cont=contact
            cont.statut=2
            cont.save()
        
    if request.method=="POST":
        subject=request.POST["subject"]
        content=request.POST["content"]
        dic={}

        dic["user1"]=id
        dic["user2"]=request.user.id

        contact=Contact(
            name="",
            email="",
            subject=subject,
            datecontact= date,
            statut=0,
            status=1,
            message=content,
            codes=dic
        )
        contact.save()
        return redirect("contact/detmes",id=id)

    tabMessage=[]
    contacts=Contact.objects.filter(statut__in=[0,1,2], status=1).order_by("-id")
    for contact in contacts:
        codes=eval(contact.codes)
        if codes["user1"]==request.user.id and codes["user2"]==id or codes["user1"]==id and codes["user2"]==request.user.id:
            
            dic={}
            #On verifie si le membre connecté est le recepteur
            if codes["user1"]==request.user.id:
                # On verifie si le message a été supprimé ou pas
                if contact.statutdel == 0 or contact.statutdel == 1:
                    user=User.objects.get(id=codes["user2"])
                    dic["code"]=contact.id
                    dic["status"]=0
                    dic["id"]=user.id
                    dic["lastname"]=user.last_name
                    dic["firstname"]=user.first_name
                    dic["message"]=contact.message
                    dic["datecontact"]=contact.datecontact
                    tabMessage.append(dic)
            else:
                # On verifie si le message a été supprimé ou pas
                if contact.statutdel == 0 or contact.statutdel == 2:
                    user=User.objects.get(id=codes["user1"])
                    dic["code"]=contact.id
                    dic["status"]=1
                    dic["id"]=user.id
                    dic["lastname"]="vous"
                    dic["message"]=contact.message
                    dic["datecontact"]=contact.datecontact
                    tabMessage.append(dic)

    context={
        "user":user,
        "contacts":tabMessage,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "contact/detmes.html", context)

#=================== Gestion de l'établissemnt ======================
@login_required(login_url='connection/login')
def etablissements(request):
    date=datetime.datetime.now()

    etablissements=Etablissement.objects.filter(user_id=request.user.id)
    context={
        "etablissements":etablissements,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "etablissement/etablissements.html", context)

@login_required(login_url='connection/login')
@csrf_exempt
def add_etab(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        name=request.POST["name"]
        country=request.POST["country"]
        city=request.POST["city"]

        query=Etablissement.objects.filter(name=name, user_id=request.user.id)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            etablissement=Etablissement(name=name,country=country,city=city,user_id=request.user.id)
            etablissement.save()
            return JsonResponse({'status':'Save'})

    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "etablissement/add_etab.html", context)

@login_required(login_url='connection/login')
def edit_etab(request,id):
    date=datetime.datetime.now()
    etablissement=Etablissement.objects.get(id=id)
    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Etablissement.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "etablissement":etablissement,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "etablissement/edit_etab.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_eta(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            etablissement=Etablissement.objects.get(id=id)
        except:
            etablissement=None
        
        if etablissement == None:
            return JsonResponse({'status':1})
        else:
            name=request.POST["name"]
            country=request.POST["country"]
            city=request.POST["city"]
            #On exclut l'établissement' que l'on veut modifier et on recupère les autres
            etablissements=Etablissement.objects.exclude(id=id)
            tabEtablissement=[]
            for etab in etablissements:
                try:
                    if etab.user.id == request.user.id:
                        tabEtablissement.append(etab.name)
                except Exception as e:
                    pass
            #On verifie si cet établissement existe déjà
            if name in tabEtablissement:
                return JsonResponse({'status':0})
            else:
                etablissement.name=name
                etablissement.country=country
                etablissement.city=city
                etablissement.save()
                return JsonResponse({'status':'Save'})


@login_required(login_url='connection/login')
def del_etab(request,id):
    etablissement=Etablissement.objects.get(id=id)
    etablissement.delete()
    return redirect("etablissement/etablissements")


#=================== Gestion de formation ======================
@login_required(login_url='connection/login')
def formations(request):
    date=datetime.datetime.now()

    formations=Formation.objects.filter(user_id=request.user.id)
    context={
        "formations":formations,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "formation/formations.html", context)

@login_required(login_url='connection/login')
@csrf_exempt
def add_form(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        intitule=request.POST["intitule"]
        query=Formation.objects.filter(intitule=intitule,user_id=request.user.id)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            count0=Formation.objects.all().count()
            formation=Formation(intitule=intitule,user_id=request.user.id)
            formation.save()
            count1=Formation.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
               return JsonResponse({'status':1}) 

    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "formation/add_form.html", context)

@login_required(login_url='connection/login')
def edit_form(request,id):
    date=datetime.datetime.now()
    formation=Formation.objects.get(id=id)
    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Formation.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "formation":formation,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "formation/edit_form.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_for(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            formation=Formation.objects.get(id=id)
        except:
            formation=None

        if formation == None:
            return JsonResponse({'status':1}) 
        else:
            intitule=request.POST["intitule"]
            #On exclut la formation que l'on veut modifier et on recupère les autres
            formations=Formation.objects.exclude(id=id)
            tabFormation=[]
            for form in formations:
                try:
                    if form.user.id == request.user.id:
                        tabFormation.append(form.intitule)
                except Exception as e:
                        pass
            #On verifie si cette formation existe déjà
            if intitule in tabFormation:
                return JsonResponse({'status':0})
            else:
                formation.intitule=intitule
                formation.save()
                return JsonResponse({'status':'Save'})

@login_required(login_url='connection/login')
def del_form(request,id):
    formation=Formation.objects.get(id=id)
    formation.delete()
    return redirect("formation/formations")

#=================== Gestion de l'entreprise ======================
@login_required(login_url='connection/login')
def entreprises(request):
    date=datetime.datetime.now()

    entreprises=Entreprise.objects.filter(user_id=request.user.id)
    context={
        "entreprises":entreprises,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "entreprise/entreprises.html", context)

@login_required(login_url='connection/login')
@csrf_exempt
def add_ent(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        name=request.POST["name"]
        country=request.POST["country"]
        city=request.POST["city"]
        query=Entreprise.objects.filter(name=name,user_id=request.user.id)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            count0=Entreprise.objects.all().count()
            entreprise=Entreprise(name=name,country=country,city=city, user_id=request.user.id)
            entreprise.save()
            count1=Entreprise.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
                return JsonResponse({'status':1})

    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "entreprise/add_ent.html", context)

@login_required(login_url='connection/login')
def edit_ent(request,id):
    date=datetime.datetime.now()
    entreprise=Entreprise.objects.get(id=id)
    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Entreprise.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "entreprise":entreprise,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "entreprise/edit_ent.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_en(request):
    
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            entreprise=Entreprise.objects.get(id=id)
        except:
            entreprise=None

        if entreprise == None:
            return JsonResponse({'status':1})
        else:
            name=request.POST["name"]
            country=request.POST["country"]
            city=request.POST["city"]

            #On exclut l'entreprise' que l'on veut modifier et on recupère les autres
            entreprises=Entreprise.objects.exclude(id=id)
            tabEntreprise=[]
            for ent in entreprises:
                try:
                    if ent.user.id == request.user.id:
                        tabEntreprise.append(ent.name)
                except Exception as e:
                    pass
            #On verifie si cette entreprise existe déjà
            if name in tabEntreprise:
                return JsonResponse({'status':0})
            else:
                entreprise.name=name
                entreprise.country=country
                entreprise.city=city
                entreprise.save()
                return JsonResponse({'status':'Save'})

@login_required(login_url='connection/login')
def del_ent(request,id):
    date=datetime.datetime.now()

    entreprise=Entreprise.objects.get(id=id)
    if request.method=="POST":
        entreprise.delete()
        return redirect("entreprise/entreprises")

    context={
        "entreprise":entreprise,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "entreprise/del_ent.html", context)

#=================== Gestion de parcours ======================
@login_required(login_url='connection/login')
def parcours(request):
    date=datetime.datetime.now()

    parcours=Parcours.objects.filter(user_id=request.user.id).order_by('annee_id')

    context={
        "parcours":parcours,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "parcours/parcours.html", context)

@login_required(login_url='connection/login')
@csrf_exempt
def add_parcours(request):
    date=datetime.datetime.now()

    if request.method=="POST":
            annee=request.POST["annee"]
            annee1=request.POST["annee1"]

            user=request.user.id
            etablissement=request.POST["etablissement"]
            formation=request.POST["formation"]
            niveau=request.POST["niveau"]
            query=Parcours.objects.filter(etablissement_id=etablissement, annee_id=annee, user_id=request.user.id)
            if query.exists():
                return JsonResponse({'status':0})
            else:
                parcours=Parcours(
                    niveau=niveau,
                    annee_id=annee,
                    annee1=annee1,
                    etablissement_id=etablissement,
                    formation_id=formation,
                    user_id=user,
                    status=0
                )
                count0=Parcours.objects.all().count()
                parcours.save()
                count1=Parcours.objects.all().count()
                if count0 < count1:
                    return JsonResponse({'status':'Save'})
                else:
                    return JsonResponse({'status':1})

    annees=Annee.objects.all().order_by("-libelle")
    etablissements=Etablissement.objects.filter(user_id=request.user.id)
    formations=Formation.objects.filter(user_id=request.user.id)

    context={
        "etablissements":etablissements,
        "formations":formations,
        "annees":annees,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "parcours/add_parcours.html", context)

@login_required(login_url='connection/login')
def edit_parcours(request,id):
    date=datetime.datetime.now()
    parcours=Parcours.objects.get(id=id)
    annees=Annee.objects.all()
    etablissements=Etablissement.objects.filter(user_id=request.user.id)
    formations=Formation.objects.filter(user_id=request.user.id)
    tabannee=[]
    for annee in annees:
        if int(annee.libelle) > int(parcours.annee.libelle):
            tabannee.append(annee)

    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Parcours.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "etablissements":etablissements,
            "formations":formations,
            "parcours":parcours,
            "annees":annees, 
            "tabannee":tabannee,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "parcours/edit_parcours.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_par(request): 
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            parcours=Parcours.objects.get(id=id)
        except:
            parcours=None

        if parcours == None:
            return JsonResponse({'status':1})
        else:    
            annee=request.POST["annee"]
            annee1=request.POST["annee1"]
            etablissement=request.POST["etablissement"]
            formation=request.POST["formation"]
            niveau=request.POST["niveau"]
            status=request.POST["status"]
            #On exclut le parcours que l'on veut modifier et on recupère les autres
            list_parcours=Parcours.objects.exclude(id=id)
            
            tabParcours=[]
            for parcour in list_parcours:
                try:
                    if parcour.user.id == request.user.id :
                        tabParcours.append(parcour)
                except Exception as e:
                    pass

            #On verifie si ce parcours existe déjà
            x=False
            for p in tabParcours:
                if int(annee) == p.annee.id and int(etablissement) == p.etablissement.id:
                    x=True
            if x :
                return JsonResponse({'status':0})
            else:
                parcours.annee_id=annee
                parcours.annee1=annee1
                parcours.etablissement_id=etablissement
                parcours.formation_id=formation
                parcours.niveau=niveau
                parcours.statusan=status
                
                parcours.save()
            return JsonResponse({'status':'Save'})


@login_required(login_url='connection/login')
def del_parcours(request,id):
    parcours=Parcours.objects.get(id=id)
    parcours.delete()
    return redirect("parcours/parcours")

class fetchpar(View):
    def get(self, request, id, *args, **kwargs):
        #On compte le nombre de matière qui ne sont pas publiées
        parcoursNoActif=Parcours.objects.values("etablissement_id","annee_id","annee1").filter(annee_id=id,user_id=request.user.id,status=0).annotate(effectif=Count("annee_id"))
        #On compte le nombre de matière qui sont publiées
        parcoursActif=Parcours.objects.values("etablissement_id","annee_id","annee1").filter(annee_id=id,user_id=request.user.id,status=1).annotate(effectif=Count("annee_id"))

        countMatiereNoActif=0
        for parcour in parcoursNoActif:
            countMatiereNoActif+=parcour["effectif"]

        countMatiereActif=0
        for parcour in parcoursActif:
            countMatiereActif+=parcour["effectif"]

        countpar=countMatiereActif + countMatiereNoActif

        context={
            "countpar":countpar,
            "countactif":countMatiereActif,
            "countNoactif":countMatiereNoActif
        }
        return render(request, "fetchpar.html", context)

class getFormParcours(View):
    def get(self, request, id, *args, **kwargs):
        
        type_exp=id
        status=False
        if type_exp=="Employé(e)":
            status=True

        context={
            "status":status
        }
        return render(request, "ajax.html", context)

class getFormParcours2(View):
    def get(self, request, id, *args, **kwargs):
        
        type_exp=id
        status=False
        if type_exp=="Employé(e)":
            status=True

        context={
            "status":status
        }
        return render(request, "ajax.html", context)
    
class getFormAnnee(View):
    def get(self, request, id, *args, **kwargs):
        
        tabAnnees=[]
        annee=Annee.objects.get(id=id)
        annees=Annee.objects.all()

        for anne in annees:
            if int(anne.libelle) > int(annee.libelle):
                tabAnnees.append(anne)

        context={
            "annees":tabAnnees
        }
        return render(request, "ajaxAnnee.html", context)
    
class status(View):
    def get(self, request, id, *args, **kwargs):
        return JsonResponse({'status':id})

    
class getFormAnnee2(View):
    def get(self, request, id, *args, **kwargs):
        
        tabAnnees=[]
        annee=Annee.objects.get(id=id)
        annees=Annee.objects.all()

        for anne in annees:
            if int(anne.libelle) > int(annee.libelle):
                tabAnnees.append(anne)

        context={
            "annees":tabAnnees
        }
        return render(request, "ajaxAnnee.html", context)

class statpar(View):
    def get(self, request, id, *args, **kwargs):
        parcours=Parcours.objects.get(id=id)
        if parcours.status==0:
            parcours.status=1
        else:
            parcours.status=0
        parcours.save()
        context={"parcours":parcours}
        return render(request, "statpar.html", context)
    
@login_required(login_url='connection/login') 
def statistique(request):
    date=datetime.datetime.now()

    questions=Question.objects.all()

    nbjanuary=0
    nbfebruary=0
    nbmarch=0
    nbapril=0
    nbmay=0
    nbjune=0
    nbjully=0
    nbaugust=0
    nbseptember=0
    nboctober=0
    nbnovember=0
    nbdecember=0
    tabmonth=[]
    for question in questions:
        if question.date.year==date.year:
            if question.date.month == 1:
                nbjanuary+=1
            elif question.date.month == 2:
                nbfebruary+=1
            elif question.date.month == 3:
                nbmarch+=1
            elif question.date.month == 4:
                nbapril+=1
            elif question.date.month == 5:
                nbmay+=1
            elif question.date.month == 6:
                nbjune+=1
            elif question.date.month == 7:
                nbjully+=1
            elif question.date.month == 8:
                nbaugust+=1
            elif question.date.month == 9:
                nbseptember+=1
            elif question.date.month == 10:
                nboctober+=1
            elif question.date.month == 11:
                nbnovember+=1
            else:
                nbdecember+=1
    
    tabmonth.append(nbjanuary)
    tabmonth.append(nbfebruary)
    tabmonth.append(nbmarch)
    tabmonth.append(nbapril)
    tabmonth.append(nbmay)
    tabmonth.append(nbjune)
    tabmonth.append(nbjully)
    tabmonth.append(nbaugust)
    tabmonth.append(nbseptember)
    tabmonth.append(nboctober)
    tabmonth.append(nbnovember)
    tabmonth.append(nbdecember)

    #On compte le nombre de cours
    countcoursencours=Cours.objects.filter(status="Traitement en cours").count()
    countcourspublie=Cours.objects.filter(status="Cours publié").count()
    countcoursnonpublie=Cours.objects.filter(status="Cours non retenu").count()

    tabCours=[]
    tabCours.append(countcoursencours)
    tabCours.append(countcourspublie)
    tabCours.append(countcoursnonpublie)

    context={
        "coursdata":tabCours,
        "months":tabmonth,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "statistique.html",context)

#======================== Gestion de competences==============================
def competences(request):
    date=datetime.datetime.now()

    competences=Competence.objects.values("type_comp").filter(user_id=request.user.id).annotate(effectif=Count("type_comp"))
    tabCompetences=[]
    for competence in competences:
        competenceActif=Competence.objects.values("type_comp").filter(type_comp=competence["type_comp"],user_id=request.user.id,status=1).annotate(effectif=Count("type_comp"))
        competenceNoActif=Competence.objects.values("type_comp").filter(type_comp=competence["type_comp"],user_id=request.user.id,status=0).annotate(effectif=Count("type_comp"))
        
        countActif=0
        for comp in competenceActif:
            countActif+=comp["effectif"]
        
        countNoActif=0
        for comp in competenceNoActif:
            countNoActif+=comp["effectif"]
        tab={}
        tab["type_comp"]=competence["type_comp"]
        tab["effectif"]=competence["effectif"]
        tab["active"]=countActif
        tab["noactive"]=countNoActif
        tabCompetences.append(tab)

    context={
        "competences":tabCompetences,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "competence/competences.html",context)


@login_required(login_url='connection/login')
@csrf_exempt
def add_comp(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        type_comp=request.POST["type_comp"]
        name=request.POST["name"]
        comment=request.POST["comment"]
        query=Competence.objects.filter(name=name, user_id=request.user.id)
        if query.exists():
            return JsonResponse({'status':0})
        else:
            competence=Competence(type_comp=type_comp,name=name,comment=comment,user_id=request.user.id,status=False)
            count0=Competence.objects.all().count()
            competence.save()
            count1=Competence.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
                return JsonResponse({'status':1})
    context={
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "competence/add_comp.html", context)

@login_required(login_url='connection/login')
def del_comp(request,id):
    competence=Competence.objects.get(id=id)
    competence.delete()
    return redirect("competence/details_comp", id=competence.type_comp)

@login_required(login_url='connection/login')
def delete_comp(request,id):
    competences=Competence.objects.filter(id=id, user_id=request.user.id)
    for competence in competences:
        competence.delete()
    return redirect("competence/details_comp", id=competence.type_comp)

@login_required(login_url='connection/login')
def details_comp(request, id):
    date=datetime.datetime.now()
    competences=Competence.objects.filter(type_comp=id, user_id=request.user.id)
    context={
        "competence":id,
        "competences":competences,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "competence/details_comp.html",context)

@login_required(login_url='connection/login')
def edit_comp(request,id):
    date=datetime.datetime.now()
    competence=Competence.objects.get(id=id)
    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Competence.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "competence":competence,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "competence/edit_comp.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_cmp(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            competence=Competence.objects.get(id=id)
        except:
            competence=None
        
        if competence == None:
            return JsonResponse({'status':0})
        else:
            type_comp=request.POST["type_comp"]
            name=request.POST["name"]
            comment=request.POST["comment"]
            #On exclut la compétence que l'on veut modifier et on recupère les autres
            competences=Competence.objects.exclude(id=id)
            tabCompetence=[]
            for comp in competences:
                try:
                    if comp.user.id == request.user.id:
                        tabCompetence.append(comp.name)
                except Exception as e:
                    pass
            #On verifie si cette compétence existe déjà
            if name in tabCompetence:
                return JsonResponse({'status':0})
            else:
                competence.type_comp=type_comp
                competence.name=name
                competence.comment=comment
                competence.save()
                return JsonResponse({'status':'Save'})


class statcomp(View):
    def get(self, request, id, *args, **kwargs):
        competence=Competence.objects.get(id=id)
        if competence.status==0:
            competence.status=1
        else:
            competence.status=0
        competence.save()

        context={"competence":competence}
        return render(request, "statcomp.html", context)

class fetchcomp(View):
    def get(self, request, id, *args, **kwargs):

        competenceActif=Competence.objects.values("type_comp").filter(type_comp=id,user_id=request.user.id,status=1).annotate(effectif=Count("type_comp"))
        competenceNoActif=Competence.objects.values("type_comp").filter(type_comp=id,user_id=request.user.id,status=0).annotate(effectif=Count("type_comp"))
        
        countActif=0
        for comp in competenceActif:
            countActif+=comp["effectif"]
        
        countNoActif=0
        for comp in competenceNoActif:
            countNoActif+=comp["effectif"]

        countcomp=countActif+countNoActif

        context={
            "countcomp":countcomp,
            "countactif":countActif,
            "countNoactif":countNoActif
        }
        return render(request, "fetchcomp.html", context)

class ajaxcomp(View):
    def get(self, request, id, *args, **kwargs):
    
        context={
            "type_comp":id
        }
        return render(request, "ajaxcomp.html", context)

@login_required(login_url='connection/login')
def recap(request):
    date=datetime.datetime.now()
    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=request.user.id, status=1).order_by("-annee_id")
    countpar=Parcours.objects.filter(user_id=request.user.id, status=1).count()
    #======== Competence ==============
    competenceLangages=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1)
    cpLangage=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1).count()

    competenceFrameworks=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1)
    cpFramework=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1).count()

    competenceSystemes=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1)
    cpSysteme=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1).count()

    competenceSE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1)
    cpSystemeE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1).count()

    competenceLogiciels=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1)
    cpLogiciel=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1).count()

    competenceModelisations=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1)
    cpModelisation=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1).count()

    competenceOE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1)
    cpOutilsE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1).count()

    competenceBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1)
    cpBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1).count()

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1).count()

    countcomp=Competence.objects.filter(user_id=request.user.id, status=1).count()
    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=request.user.id, status=1)
    countexp=Experience.objects.filter(user_id=request.user.id, status=1).count()

    context={
        "countpar":countpar,
        "countexp":countexp,
        "countcomp":countcomp,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competenceLangages":competenceLangages,
        "cpLangage":cpLangage,
        "competenceFrameworks":competenceFrameworks,
        "cpFramework":cpFramework,
        "competenceSystemes":competenceSystemes,
        "cpSysteme":cpSysteme,
        "competenceSE":competenceSE,
        "cpSystemeE":cpSystemeE,
        "competenceLogiciels":competenceLogiciels,
        "cpLogiciel":cpLogiciel,
        "competenceModelisations":competenceModelisations,
        "cpModelisation":cpModelisation,
        "competenceOE":competenceOE,
        "cpOutilsE":cpOutilsE,
        "competenceBureautique":competenceBureautique,
        "cpBureautique":cpBureautique,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "cv/recap.html", context)

@login_required(login_url='connection/login')
def recap_1(request):
    date=datetime.datetime.now()
    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=request.user.id, status=1).order_by("-annee_id")
    countpar=Parcours.objects.filter(user_id=request.user.id, status=1).count()
    #======== Competence ==============
    tabCompetences=[]
    competences=Competence.objects.filter(user_id=request.user.id, status=1)
    countcomp=0
    for competence in competences:
        if competence.type_comp == "Langue" or competence.type_comp == "Loisir":
            pass
        else:
            countcomp+=1
            tabCompetences.append(competence)

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1).count()
    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=request.user.id, status=1)
    countexp=Experience.objects.filter(user_id=request.user.id, status=1).count()

    context={
        "countpar":countpar,
        "countexp":countexp,
        "countcomp":countcomp,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competences":tabCompetences,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "cv/recap-1.html", context)


def cv(request,id):
    date=datetime.datetime.now()
    user=User.objects.get(id=id)

    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=id).order_by("-annee_id")
    countpar=Parcours.objects.filter(user_id=id).count()
    #======== Competence ==============
    competenceLangages=Competence.objects.filter(type_comp="Langage de programmation", user_id=id, status=1)
    cpLangage=Competence.objects.filter(type_comp="Langage de programmation", user_id=id, status=1).count()

    competenceFrameworks=Competence.objects.filter(type_comp="Framework", user_id=id, status=1)
    cpFramework=Competence.objects.filter(type_comp="Framework", user_id=id, status=1).count()

    competenceSystemes=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=id, status=1)
    cpSysteme=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=id, status=1).count()

    competenceSE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=id, status=1)
    cpSystemeE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=id, status=1).count()

    competenceLogiciels=Competence.objects.filter(type_comp="Logiciel", user_id=id, status=1)
    cpLogiciel=Competence.objects.filter(type_comp="Logiciel", user_id=id, status=1).count()

    competenceModelisations=Competence.objects.filter(type_comp="Modélisation", user_id=id, status=1)
    cpModelisation=Competence.objects.filter(type_comp="Modélisation", user_id=id, status=1).count()

    competenceOE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=id, status=1)
    cpOutilsE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=id, status=1).count()

    competenceBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=id, status=1)
    cpBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=id, status=1).count()

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=id, status=1).count()

    countcomp=Competence.objects.filter(user_id=id, status=1).count()
    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=id,status=1)
    countexp=Experience.objects.filter(user_id=id,status=1).count()

    context={
        "countpar":countpar,
        "countexp":countexp,
        "countcomp":countcomp,
        "user":user,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competenceLangages":competenceLangages,
        "cpLangage":cpLangage,
        "competenceFrameworks":competenceFrameworks,
        "cpFramework":cpFramework,
        "competenceSystemes":competenceSystemes,
        "cpSysteme":cpSysteme,
        "competenceSE":competenceSE,
        "cpSystemeE":cpSystemeE,
        "competenceLogiciels":competenceLogiciels,
        "cpLogiciel":cpLogiciel,
        "competenceModelisations":competenceModelisations,
        "cpModelisation":cpModelisation,
        "competenceOE":competenceOE,
        "cpOutilsE":cpOutilsE,
        "competenceBureautique":competenceBureautique,
        "cpBureautique":cpBureautique,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "cv/cv.html", context)

@login_required(login_url='connection/login')
def generatecv(request):
    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=request.user.id).order_by("-annee_id")
    #======== Competence ==============
    competenceLangages=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1)
    cpLangage=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1).count()

    competenceFrameworks=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1)
    cpFramework=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1).count()

    competenceSystemes=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1)
    cpSysteme=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1).count()

    competenceSE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1)
    cpSystemeE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1).count()

    competenceLogiciels=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1)
    cpLogiciel=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1).count()

    competenceModelisations=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1)
    cpModelisation=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1).count()

    competenceOE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1)
    cpOutilsE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1).count()

    competenceBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1)
    cpBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1).count()

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1).count()

    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=request.user.id, status=1)
    user=User.objects.get(id=request.user.id)
    context={
        "user":user,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competenceLangages":competenceLangages,
        "cpLangage":cpLangage,
        "competenceFrameworks":competenceFrameworks,
        "cpFramework":cpFramework,
        "competenceSystemes":competenceSystemes,
        "cpSysteme":cpSysteme,
        "competenceSE":competenceSE,
        "cpSystemeE":cpSystemeE,
        "competenceLogiciels":competenceLogiciels,
        "cpLogiciel":cpLogiciel,
        "competenceModelisations":competenceModelisations,
        "cpModelisation":cpModelisation,
        "competenceOE":competenceOE,
        "cpOutilsE":cpOutilsE,
        "competenceBureautique":competenceBureautique,
        "cpBureautique":cpBureautique,
        'domain':get_current_site(request).domain,
    }
    template=get_template("cv/generatecv.html")
    html=template.render(context)
    options={
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    pdf=pdfkit.from_string(html, False, options)
    reponse = HttpResponse(pdf, content_type='application/pdf')
    reponse['Content-Disposition']="attachement"
    return reponse

@login_required(login_url='connection/login')
def generatecv_1(request):
    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=request.user.id).order_by("-annee_id")
    #======== Competence ==============
    tabCompetences=[]
    competences=Competence.objects.filter(user_id=request.user.id, status=1)
    countcomp=0
    for competence in competences:
        if competence.type_comp == "Langue" or competence.type_comp == "Loisir":
            pass
        else:
            countcomp+=1
            tabCompetences.append(competence)

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1).count()

    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=request.user.id, status=1)
    user=User.objects.get(id=request.user.id)
    context={
        "user":user,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competences":tabCompetences,
        "countcomp":countcomp,
        'domain':get_current_site(request).domain,
    }
    template=get_template("cv/generatecv-1.html")
    html=template.render(context)
    options={
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    pdf=pdfkit.from_string(html, False, options)
    reponse = HttpResponse(pdf, content_type='application/pdf')
    reponse['Content-Disposition']="attachement"
    return reponse

@login_required(login_url='connection/login')
def profuser(request,id):
    date=datetime.datetime.now()
    user=User.objects.get(id=id)

    #======== Parcours ===============
    parcours=Parcours.objects.filter(user_id=id, status=1).order_by("-annee_id")
    countpar=Parcours.objects.filter(user_id=id).count()
    #======== Competence ==============
    competenceLangages=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1)
    cpLangage=Competence.objects.filter(type_comp="Langage de programmation", user_id=request.user.id, status=1).count()

    competenceFrameworks=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1)
    cpFramework=Competence.objects.filter(type_comp="Framework", user_id=request.user.id, status=1).count()

    competenceSystemes=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1)
    cpSysteme=Competence.objects.filter(type_comp="Système de Gestion de Base de Données", user_id=request.user.id, status=1).count()

    competenceSE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1)
    cpSystemeE=Competence.objects.filter(type_comp="Système d'exploitation", user_id=request.user.id, status=1).count()

    competenceLogiciels=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1)
    cpLogiciel=Competence.objects.filter(type_comp="Logiciel", user_id=request.user.id, status=1).count()

    competenceModelisations=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1)
    cpModelisation=Competence.objects.filter(type_comp="Modélisation", user_id=request.user.id, status=1).count()

    competenceOE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1)
    cpOutilsE=Competence.objects.filter(type_comp="Outil et Environnement", user_id=request.user.id, status=1).count()

    competenceBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1)
    cpBureautique=Competence.objects.filter(type_comp="Bureautique", user_id=request.user.id, status=1).count()

    competenceLangues=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1)
    cpLangue=Competence.objects.filter(type_comp="Langue", user_id=request.user.id, status=1).count()

    competenceLoisirs=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1)
    cpLoisir=Competence.objects.filter(type_comp="Loisir", user_id=request.user.id, status=1).count()

    countcomp=Competence.objects.filter(user_id=id, status=1).count()
    #======================= Expérience professionnelle=====================
    experiences=Experience.objects.filter(user_id=id,status=1)
    countexp=Experience.objects.filter(user_id=id,status=1).count()
    context={
        "countpar":countpar,
        "countexp":countexp,
        "countcomp":countcomp,
        "user":user,
        "parcours":parcours,
        "experiences":experiences,
        "competenceLangues":competenceLangues,
        "cpLangue":cpLangue,
        "competenceLoisirs":competenceLoisirs,
        "cpLoisir":cpLoisir,
        "competenceLangages":competenceLangages,
        "cpLangage":cpLangage,
        "competenceFrameworks":competenceFrameworks,
        "cpFramework":cpFramework,
        "competenceSystemes":competenceSystemes,
        "cpSysteme":cpSysteme,
        "competenceSE":competenceSE,
        "cpSystemeE":cpSystemeE,
        "competenceLogiciels":competenceLogiciels,
        "cpLogiciel":cpLogiciel,
        "competenceModelisations":competenceModelisations,
        "cpModelisation":cpModelisation,
        "competenceOE":competenceOE,
        "cpOutilsE":cpOutilsE,
        "competenceBureautique":competenceBureautique,
        "cpBureautique":cpBureautique,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "cv/profuser.html", context)


#=================== Gestion de l'experience ======================
@login_required(login_url='connection/login')
def experiences(request):
    date=datetime.datetime.now()

    experiences=Experience.objects.filter(user_id=request.user.id)
    context={
        "experiences":experiences,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "experience/experiences.html", context)

@login_required(login_url='connection/login')
@csrf_exempt
def add_exp(request):
    date=datetime.datetime.now()

    if request.method=="POST":
        type_exp=request.POST["type_exp"]
        entreprise=request.POST["entreprise"]
        date_debut=request.POST["date_debut"]
        date_fin=request.POST["date_fin"]

        if date_debut > date_fin:
            return JsonResponse({'status':2})
        else:
            query=Experience.objects.filter(date_debut=date_debut,date_fin=date_fin,user_id=request.user.id)
            if query.exists():
                return JsonResponse({'status':0})
            else:
                if type_exp=="Employé(e)":
                    posteoccupe=request.POST["posteoccupe"]
                    projet_mission=request.POST["projet_mission"]
                    title=request.POST["title"]
                    experience=Experience(
                        type_exp=type_exp,
                        posteoccupe=posteoccupe,
                        projet_mission=projet_mission,
                        titl=title,
                        tache="",
                        date_debut=date_debut,
                        date_fin=date_fin,
                        entreprise_id=entreprise,
                        user_id=request.user.id
                    )
                    count0=Experience.objects.all().count()
                    experience.save()
                    count1=Experience.objects.all().count()
                    if count0 < count1:
                        return JsonResponse({'status':'Save'})
                    else:
                        return JsonResponse({'status':1})
                else:
                    tache=request.POST["tache"]
                    projet=request.POST["projet"]
                    
                    experience=Experience(
                        type_exp=type_exp,
                        posteoccupe="",
                        title=projet,
                        tache=tache,
                        date_debut=date_debut,
                        date_fin=date_fin,
                        entreprise_id=entreprise,
                        user_id=request.user.id
                    )
                    count0=Experience.objects.all().count()
                    experience.save()
                    count1=Experience.objects.all().count()
                    if count0 < count1:
                        return JsonResponse({'status':'Save'})
                    else:
                        return JsonResponse({'status':0})

    entreprises=Entreprise.objects.filter(user_id=request.user.id)

    context={
        "entreprises":entreprises,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date
    }
    return render(request, "experience/add_exp.html", context)

@login_required(login_url='connection/login')
def edit_exp(request,id):
    date=datetime.datetime.now()
    experience=Experience.objects.get(id=id)
    entreprises=Entreprise.objects.filter(user_id=request.user.id)
    status=0
    if experience.type_exp=="Employé(e)":
        status=1

    #On vérifie si ce membre est authorisé à acceder à cette page ou pas.
    query=Experience.objects.filter(id=id,user_id=request.user.id)
    if query.exists():
        context={
            "status":status,
            "experience":experience,
            "entreprises":entreprises,
            "countanswer":nbnew_answer(request),
            "count":nbnew_message(request),
            "users":new_message(request),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "experience/edit_exp.html", context)
    else:
        return redirect("authorization")

@login_required(login_url='connection/login')
@csrf_exempt
def edit_ex(request):
    if request.method=="POST":
        id=int(request.POST["id"])
        try:
            experience=Experience.objects.get(id=id)
        except:
            experience=None
        
        if experience == None:
            return JsonResponse({'status':1})
        else:
            type_exp=request.POST["type_exp"]
            entreprise=request.POST["entreprise"]
            date_debut=request.POST["date_debut"]
            date_fin=request.POST["date_fin"]
            if date_debut > date_fin:
                return JsonResponse({'status':2})
            else:
                #On verifie si l'experience avec les dates renseignées a été déjà enregistrée
                query=Experience.objects.filter(date_debut=date_debut,date_fin=date_fin,user_id=request.user.id).exclude(id=id)    
                if query.exists():
                    return JsonResponse({'status':0}) 
                else:
                    if type_exp=="Employé(e)":
                        posteoccupe=request.POST["posteoccupe"]
                        projet_mission=request.POST["projet_mission"]
                        title=request.POST["title"]

                        experience.type_exp=type_exp
                        experience.posteoccupe=posteoccupe
                        experience.projet_mission=projet_mission
                        experience.date_debut=date_debut
                        experience.date_fin=date_fin
                        experience.entreprise_id=entreprise
                        experience.title=title
                        
                        experience.save()
                        return JsonResponse({'status':'Save'})
                    else:
                        tache=request.POST["tache"]
                        projet=request.POST["projet"]

                        experience.type_exp=type_exp
                        experience.posteoccupe=""
                        experience.title=projet
                        experience.tache=tache
                        experience.date_debut=date_debut
                        experience.date_fin=date_fin
                        experience.entreprise_id=entreprise

                        experience.save()
                        return JsonResponse({'status':'Save'})

@login_required(login_url='connection/login')
def del_exp(request,id):
    experience=Experience.objects.get(id=id)
    experience.delete()
    return redirect("experience/experiences")

class statexp(View):
    def get(self, request, id, *args, **kwargs):
        experience=Experience.objects.get(id=id)
        if experience.status==0:
            experience.status=1
        else:
            experience.status=0
        experience.save()
        context={"experience":experience}
        return render(request, "statexp.html", context)
