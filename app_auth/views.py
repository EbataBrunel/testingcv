from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views import View
from .forms import*
from eab.utils import send_email_with_html_body
from eab.models import*
from forum.models import*
from django.db import transaction
from .decorator import*
from .tokens import account_activation_token
from django.http import JsonResponse
import datetime

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
        answers=Answer.objects.filter(question_id=question.id, status=0)
        #On exlu les reponses de ce membre qui a posé la question
        for answer in answers:
            if answer.user_id != request.user.id:
                number+=1
    return number

#Activation du compte
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Activation effectuée avec succès. Vous pouvez alors vous connecter.")
        return redirect("connection/connexion")
    else:
         messages.error(request, "Le lien d'activation est invalide")

    return redirect("connection/connexion")

#@transaction.atomic
def register(request):
    form=UserForm()
    date=datetime.datetime.now()

    if request.method=="POST":
        form=UserForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get("email")
            query=User.objects.filter(email=email)
            if query.exists():
                messages.error(request, "L'adresse e-mail renseignée existe déjà.") 
            else:
                count0=User.objects.all().count()
                user=form.save() 
                
                group=Group.objects.get(name="users/customer")
                user.groups.add(group)
                #On desactive l'accès du membre
                user.is_active=False
                user.save()
                #On recupere nombre total des membres après la création du compte
                count1=User.objects.all().count()
                #On envoie l'e-mail au membre pour activer son compte
                subject="Activation de compte"
                template="email/emailactivation.html"
                receivers = [email]
                    
                context = {
                        'domain':get_current_site(request).domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':account_activation_token.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                        'user':user,
                        'date': date,
                        'parametre': parametre()
                }
                has_send = send_email_with_html_body(
                    subjet=subject,
                    receivers=receivers,
                    template=template,
                    context=context
                )
                
                if count0 < count1 and has_send == True:
                    return redirect("users/success-account",id=user.id)
                else:
                    messages.error(request, "Inscription a échouée.")
                    context={
                        "form":form,
                        "userpriorities":userPriority(),
                        "parametre":parametre()
                    }
                    return render(request, "users/register.html", context) 
        else:
            messages.error(request, form.errors)
            context={
                "form":form,
                "userpriorities":userPriority(),
                "parametre":parametre()
            }
            return render(request, "users/register.html", context)

    context={"form":form,"userpriorities":userPriority(),"parametre":parametre,"date":date}
    return render(request, "users/register.html", context)

def success_account(request, id):
    user=User.objects.get(id=id)
    context={
        "user":user,
        "parametre":parametre()
    }
    return render(request,"users/success-account.html", context)

def login_user(request):
    #Destruction de la session
    logout(request)
    date=datetime.datetime.now()
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
            user=authenticate(username=username, password=password)
            if user is not None:
                group=user.groups.all()
                for g in group:    
                    if g.name == "admin":
                        if user.is_staff:
                            login(request, user)
                            return redirect("dashboard")
                        else:
                            messages.error(request, "Vous n'avez pas de permission")
                            return render(request, "connection/login.html", {"form":form,"parametre":parametre(),"date":date})

            messages.error(request, "Erreur d'authentification")
            return render(request, "connection/login.html", {"form":form,"parametre":parametre(),"date":date})
        else:
            for field in form.errors:
                form[field].field.widget.attrs['class']+='is-invalid'
            return render(request, "connection/login.html", {"form":form,"parametre":parametre(),"date":date})
    else:
        form=LoginForm()
        return render(request, "connection/login.html",{"form":form,"parametre":parametre(),"date":date})

def login_customer(request):
    #Destruction de la session
    logout(request)
    date=datetime.datetime.now()
    if request.method=="POST":
        form=LoginForm(request.POST)
        context={
            "form":form,
            "userpriorities":userPriority(),
            "parametre":parametre(),
            "date":date
        }
        if form.is_valid():
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
            user=authenticate(username=username, password=password)
            if user is not None:
                group=user.groups.all()
                for g in group:    
                    if g.name == "customer":
                        login(request, user)
                        return redirect("dashboard")
               
            messages.error(request, "Erreur d'authentification")
            return render(request, "connection/connexion.html", context)
        else:
            for field in form.errors:
                form[field].field.widget.attrs['class']+='is-invalid'
            return render(request, "connection/connexion.html", context)
    else:
        form=LoginForm()
        context={
            "form":form,
            "userpriorities":userPriority(),
            "parametre":parametre(),
            "date":date
        }
        return render(request, "connection/connexion.html",context)

 
@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def users(request):
    date=datetime.datetime.now()

    tabusers=[]
    users=User.objects.all()
    for user in users:
        if user.groups.exists():
            group=user.groups.all()[0].name
            if group=="admin":
                tabusers.append(user)
    context={
        "tabusers":tabusers,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/users.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def detail_user(request,id):
    date=datetime.datetime.now()
    user=User.objects.get(id=id)
    context={
        "user":user,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/detail_user.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def del_user(request,id):
    user=User.objects.get(id=id)
    user.delete()
    return redirect("users/users")

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def customers(request):
    date=datetime.datetime.now()

    tabusers=[]
    users=User.objects.all()
    for user in users:
        if user.groups.exists():
            group=user.groups.all()[0].name
            if group=="customer":
                tabusers.append(user)
    context={
        "tabusers":tabusers,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/customers.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def details_cus(request,id):
    date=datetime.datetime.now()

    user=User.objects.get(id=id)
    context={
        "user":user,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/details_cus.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def del_customer(request,id):
    user=User.objects.get(id=id)
    user.delete()
    return redirect("users/customers")

@login_required(login_url='connection/login')
def profile(request):
    date=datetime.datetime.now()
    try:
        profile=Profile.objects.get(user=request.user)
    except Exception as e:
        profile=None

    if request.method=="POST":
        photo=None
        if request.POST.get('photo', True):
            photo = request.FILES["photo"]
        if photo is not None :
            profile.photo=photo
            profile.save()
            return redirect("users/profile")            
        return redirect("users/profile")
    
    context={
        "profile":profile,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request,"users/profile.html",context)

@login_required(login_url='connection/login')
@transaction.atomic
def edit_profile(request):
    date=datetime.datetime.now()

    try:
        profile=Profile.objects.get(user=request.user)
    except Exception as e:
        profile=None
     
    if request.method=="POST":
        #On verifie si le profile n'existe pour le créer sinon on le modifie.
        if profile==None:
            nom=request.POST["nom"]
            prenom=request.POST["prenom"]
            gender=request.POST["gender"]
            email=request.POST["email"]
            adresse=request.POST["adresse"]
            phone=request.POST["phone"]
            profession=request.POST["profession"]

            request.user.last_name=nom
            request.user.first_name=prenom
            request.user.email=email

            with transaction.atomic():
                request.user.save()
                profil=Profile(phone=phone, address=adresse, user=request.user, gender=gender,profession=profession)
                profil.save()
                return redirect("users/profile")
        else:
            nom=request.POST["nom"]
            prenom=request.POST["prenom"]
            gender=request.POST["gender"]
            email=request.POST["email"]
            adresse=request.POST["adresse"]
            phone=request.POST["phone"]
            profession=request.POST["profession"]

            user=profile.user
            user.last_name=nom
            user.first_name=prenom
            user.email=email

            with transaction.atomic():
                user.save()
                profile.gender=gender
                profile.phone=phone
                profile.address=adresse
                profile.profession=profession
                profile.save()
                return redirect("users/profile")

    context={
        "profile":profile,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/edit_profile.html", context)

@login_required(login_url='connection/login')
@transaction.atomic
def configuration(request):
    date=datetime.datetime.now()

    try:
        profile=Profile.objects.get(user=request.user)
    except Exception as e:
        profile=None
     
    if request.method=="POST":
        droitmes=request.POST.get("droitmes")
        status=request.POST.get("status")
        apropos=request.POST["apropos"]
        formation=request.POST["formation"]
        competence=request.POST["competence"]
        experience=request.POST["experience"]
        autre=request.POST["autre"]
        #On verifie si le profile n'existe pas pour le créer sinon on le modifie.
        if profile==None:
            profil=Profile(
                phone="", 
                address="", 
                user=request.user, 
                gender="",
                apropos=apropos,
                droitmes=droitmes,
                status=status,
                vaform=autre,
                vcom=competence,
                vep=experience,
                vform=formation
            )
            profil.save()
            return redirect("users/configuration")
        else:
            profile.droitmes=droitmes
            profile.status=status
            profile.apropos=apropos
            profile.vform=formation
            profile.vcomp=competence
            profile.vep=experience
            profile.vaform=autre
            profile.save()
            return redirect("users/configuration")

    context={
        "profile":profile,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/configuration.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def upd_access(request, id):
    date=datetime.datetime.now()

    user=User.objects.get(id=id)
    if request.method=="POST":
        if user.is_staff==1:
            user.is_staff=0
            user.save()
            return redirect("users/users")
        else:
            user.is_staff=1
            user.save()
            return redirect("users/users")
    context={
        "user":user,
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "users/upd_access.html",context)

def logout_user(request):
    group=request.user.groups.all()
    for g in group:    
        if g.name == "admin":
            logout(request)
            for key in request.session.keys():
                del request.session[key]
            return redirect("connection/login")
        else:
            logout(request)
            for key in request.session.keys():
                del request.session[key]
            return redirect("connection/connexion")

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
def param(request):
    if request.method=="POST":
        id=request.POST["id"]
        if id !="":
            param=Parametre.objects.get(id=id)
            appname=request.POST["appname"]
            appeditor=request.POST["appeditor"]
            version=request.POST["version"]
            theme=request.POST["theme"]
            devise=request.POST["devise"]
            email=request.POST["email"]
            phone=request.POST["phone"]
            logo=None
            if request.POST.get('logo', True):
                logo=request.FILES["logo"]
            width=request.POST["width"]
            height=request.POST["height"]

            param.appname=appname
            param.appeditor=appeditor
            param.version=version
            param.theme=theme
            param.devise=devise
            param.email=email
            param.phone=phone
            if logo is not None:
                param.logo=logo
            param.width_logo=width
            param.height_logo=height

            param.save()
            return redirect("parametre")
        else:
            appname=request.POST["appname"]
            appeditor=request.POST["appeditor"]
            version=request.POST["version"]
            theme=request.POST["theme"]
            devise=request.POST["devise"]
            email=request.POST["email"]
            phone=request.POST["phone"]
            logo=request.FILES["logo"]
            width=request.POST["width"]
            height=request.POST["height"]

            param=Parametre(
                appname=appname,
                appeditor=appeditor,
                version=version,
                theme=theme,
                devise=devise,
                email=email,
                phone=phone,
                logo=logo,
                width_logo=width,
                height_logo=height)
            param.save()
            return redirect("parametre")

    date=datetime.datetime.now()

    context={
        "date":date,
        "parametre":parametre(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "parametre.html",context)

class priority(View):
    def get(self, request, id, *args, **kwargs):
        user=User.objects.get(id=id)
        profile=Profile.objects.get(user=user)
        if profile.priority == 0:
            profile.priority=1
        else:
            profile.priority=0
        profile.save()

        if profile.priority == 1:
            return JsonResponse({'status':1})
        else:
            return JsonResponse({'status':0})
        
