from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import connection




from ..models import Todo

def get_user_todos(user):
    return Todo.objects.filter(owner=user).order_by("-pub_date")[:5]

@login_required
def index(request):
    context = {"latest_todo_list": get_user_todos(request.user)}
    return render(request, "todo/index.html", context)

@login_required
def search(request):
    search_query = request.GET.get("query", "")
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, todo FROM todo_todo WHERE owner_id = {request.user.id} "
            f"AND todo LIKE '%{search_query}%'"
        )
        todos = [{"id": r[0], "todo": r[1]} for r in cursor.fetchall()]
    context = {"search_results": todos}
    return render(request, "todo/search.html", context)

# @login_required
# def search(request):
#     search_query = request.GET.get("query", "")
#     todos = Todo.objects.filter(todo__icontains=search_query, owner=request.user)
#     context = {"search_results": todos}
#     return render(request, "todo/search.html", context)


@login_required
def todo_detail(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    return render(request, "todo/todo_detail.html", {"todo": todo})

@login_required
@require_POST
def delete_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    try:
        todo.delete()
        messages.success(request, "Todo deleted successfully.")
    except Exception as e:
        messages.warning(request, f"Error deleting todo: {str(e)}")
    return redirect("/todo/")

@login_required
@require_POST
def add_todo(request):
    todo_text = request.POST.get("todo")
    if todo_text:
        new_todo = Todo(todo=todo_text, owner=request.user, pub_date=timezone.now())
        new_todo.save()
        messages.success(request, "Todo added successfully.")
    else:
        messages.warning(request, "Todo text cannot be empty.")
    next_url = request.POST.get("next")
    return redirect(next_url)

@login_required
@require_POST
def update_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    if todo is None:
        return render(request, "todo/index.html", {"message": "Todo not found.", "latest_todo_list": get_user_todos(request.user)})
    todo_text = request.POST.get("todo")
    if todo_text:
        todo.todo = todo_text
        todo.save()
        messages.success(request, "Todo updated successfully.")
    else:
        messages.warning(request, "Todo text cannot be empty.")
    next_url = request.POST.get("next")
    return redirect(next_url)

@require_POST
@login_required
def toggle_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id, owner=request.user)
    todo.completed = not todo.completed
    todo.save()
    next_url = request.POST.get("next")
    return redirect(next_url)