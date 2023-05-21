from django.shortcuts import redirect
from django.http import HttpResponse

def unauthenticated_user(views_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("connection/login")
        else:
            return views_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group=None
            if request.user.groups.exists():
                group=request.user.groups.all()[0].name
            
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("Vous n'êtes pas autorisés à acceder à cette page")
        return wrapper_func
    return decorator

def only_admin(view_func):
    def wrapper_func(request, *args, **kwargs):
        group=None
        if request.user.groups.exists():
            group=request.user.groups.all()[0].name

        if group=="customer":
            return redirect("home")   
        if group=="admin":
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("Vous n'êtes pas autorisés à acceder à cette page")
    return wrapper_func
            