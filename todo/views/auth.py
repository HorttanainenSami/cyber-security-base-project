from django.shortcuts import redirect, render
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import logging
# fix #3
file_handler = logging.FileHandler("auth.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)


def login_view(request):
    if(request.method == "GET"):
        return render(request, "todo/login.html")
    if(request.method == "POST"):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            error_message = "Invalid username or password."
            return render(request, "todo/login.html", {"error_message": error_message})

def register_view(request):
    if(request.method == "GET"):
        return render(request, "todo/register.html")
    if(request.method == "POST"):
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            return render(request, "todo/register.html", {"confirm_password_error": "Passwords do not match."})
        if User.objects.filter(username=username).exists():
            return render(request, "todo/register.html", {"error_message": "Username already exists."})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("index")

# fix #3 and #1
# def login_view(request):
#     if(request.method == "GET"):
#         return render(request, "todo/login.html")
#     if(request.method == "POST"):
#         ip = request.META.get('REMOTE_ADDR')
        
#         if cache.get(f"{ip}_attempts", 0) >= 5:
#             logging.warning(f"Too many failed login attempts from IP: {ip} for user: {request.POST.get('username')!r}")
#             error_message = "Too many failed login attempts. Please try again later."
#             return render(request, "todo/login.html", {"error_message": error_message})
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             logging.info(f"Successful login from IP: {ip} for user: {username!r}")
#             cache.set(f"{ip}_attempts", 0) 
#             login(request, user)
#             return redirect("index")
#         else:
#             cache.set(f"{ip}_attempts", cache.get(f"{ip}_attempts", 0) + 1, timeout=1*60)  
#             logging.warning(f"Failed login attempt ({cache.get(f'{ip}_attempts', 0)}) from IP: {ip} for user: {username!r}")
#             error_message = "Invalid username or password."
#             return render(request, "todo/login.html", {"error_message": error_message})


# def register_view(request):
#     if(request.method == "GET"):
#         return render(request, "todo/register.html")
#     if(request.method == "POST"):
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("confirm_password")
#         if password != confirm_password:
#             return render(request, "todo/register.html", {"confirm_password_error": "Passwords do not match."})
#         if User.objects.filter(username=username).exists():
#             return render(request, "todo/register.html", {"error_message": "Username already exists."})
#         user = User.objects.create_user(username=username, password=password)
#         logging.info(f"New user registered: {username!r} from IP: {request.META.get('REMOTE_ADDR')}")
#         login(request, user)
#         return redirect("index")

def logout_view(request):
    logout(request)
    return redirect("login")
