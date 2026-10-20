from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import logging





from .models import Todo

def get_user_todos(user):
    return Todo.objects.filter(owner=user).order_by("-pub_date")[:5]

@login_required
def index(request):
    context = {"latest_todo_list": get_user_todos(request.user)}
    return render(request, "todo/index.html", context)


def search(request):
    search_query = request.GET.get("query", "")
    todos = Todo.objects.filter(todo__icontains=search_query, owner=request.user)
    context = {"search_results": todos}
    return render(request, "todo/search.html", context)


# def login_view(request):
#     if(request.method == "GET"):
#         return render(request, "todo/login.html")
#     if(request.method == "POST"):
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect("index")
#         else:
#             error_message = "Invalid username or password."
#             return render(request, "todo/login.html", {"error_message": error_message})



def login_view(request):
    if(request.method == "GET"):
        return render(request, "todo/login.html")
    if(request.method == "POST"):
        ip = request.META.get('REMOTE_ADDR')

        if cache.get(f"{ip}_attempts", 0) >= 5:
            error_message = "Too many failed login attempts. Please try again later."
            return render(request, "todo/login.html", {"error_message": error_message})
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.set(f"{ip}_attempts", 0) 
            login(request, user)
            return redirect("index")
        else:
            cache.set(f"{ip}_attempts", cache.get(f"{ip}_attempts", 0) + 1, timeout=1*60)  
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

def logout_view(request):
    logout(request)
    return redirect("login")

@require_POST
def delete_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    try:
        todo.delete()
        message = "Todo deleted successfully."
    except Exception as e:
        message = f"Error deleting todo: {str(e)}"
    return render(request, "todo/index.html", {"message": message, "latest_todo_list": get_user_todos(request.user)}) 

@require_POST
def add_todo(request):
    if request.method == "POST":
        todo_text = request.POST.get("todo")
        if todo_text:
            new_todo = Todo(todo=todo_text, owner=request.user, pub_date=timezone.now())
            new_todo.save()
            message = "Todo added successfully."
        else:
            message = "Todo text cannot be empty."
    else:
        message = "Invalid request method."
    return render(request, "todo/index.html", {"message": message, "latest_todo_list": get_user_todos(request.user)})

def toggle_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    todo.completed = not todo.completed
    todo.save()
    return render(request, "todo/index.html", {"latest_todo_list": get_user_todos(request.user)})