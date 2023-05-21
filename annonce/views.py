from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app_auth.decorator import*
from document.views import*
from .models import*
from .forms import*

def date_actuelle():
    date=datetime.datetime.now()
    return date
def annonces(request):
    
    annonces=Annonce.objects.all().order_by("-id")
    context={
        "annonces":annonces,
        "parametre":parametre(),
        "date":date_actuelle(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
    }
    return render(request, "annonce/annonces.html", context)

@login_required(login_url='connection/login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def add_annonce(request):
    if request.method=="POST":
        #form=AnnonceForm(request.POST)
        #if form.is_valid():
            title=request.POST["title"]
            company=request.POST["company"]
            content=request.POST["content"]
            annonce=Annonce(title=title,company=company,content=content,user_id=request.user.id)
            count0=Annonce.objects.all().count()
            annonce.save()
            count1=Annonce.objects.all().count()
            if count0 < count1:
                return JsonResponse({'status':'Save'})
            else:
                return JsonResponse({'status':1}) 
        #else:
            #return JsonResponse({'status':2}) 
    form=AnnonceForm()       
    context={
        "form":form,
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request),
        "parametre":parametre(),
        "date":date_actuelle()
    }
    return render(request, "annonce/add-annonce.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_annonce(request,id):
    annonce=Annonce.objects.get(id=id)
    form = AnnonceForm()
    context={
        "form":form,
        "annonce":annonce,
        "parametre":parametre(),
        "date":date_actuelle(),
        "countanswer":nbnew_answer(request),
        "count":nbnew_message(request),
        "users":new_message(request)
    }
    return render(request, "annonce/edit-annonce.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
@csrf_exempt
def edit_ann(request):  
    if request.method=="POST":
        form=AnnonceForm(request.POST)
        if form.is_valid():
            id=int(request.POST["id"])
            try:
                annonce=Annonce.objects.get(id=id)
            except:
                annonce=None

            if annonce == None:
                return JsonResponse({'status':1})
            else:
                title=request.POST["title"]
                company=request.POST["company"]
                content=request.POST["content"]
                
                annonce.title=title
                annonce.company=company
                annonce.content=content
                annonce.save()
                return JsonResponse({'status':'Save'})
        else:
            return JsonResponse({'status':2})

def del_annonce(request, id):
    annonce=Annonce.objects.get(id=id)
    annonce.delete()
    return redirect("annonce/annonces")

def delete_annonce(request, id):
    annonce=Annonce.objects.get(id=id)
    annonce.delete()
    return redirect("annonce/annonce")

def annonce(request):

    annonces=Annonce.objects.all().order_by("-id")

    paginator = Paginator(annonces, 12)
    num_page=request.GET.get('page')
    annonces=paginator.get_page(num_page)
    
    context={
        "annonces":annonces,
        "userpriorities":userPriority(),
        "parametre":parametre(),
    }
    return render(request, "annonce/annonce.html", context)
