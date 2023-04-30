from django.http import HttpResponse
from django.shortcuts import redirect

#if a user is not authenticated then they are redirected back to the home page else they have access to the appropiate view
def unauthenticated_user(view_func):
    def wrapper_func(requests, *args, **kwargs):
        if requests.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(requests,*args, **kwargs)
    return wrapper_func


#decorator that restricts users access on certain views and webpages based on whether they are a Base User or an Manager
def allowed_users(allowed_roles = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You are not allowed to view this page")
        return wrapper_func
    return decorator


