from django.contrib import admin
from django.urls import path

from todo.views import auth, todo

urlpatterns = [
    path("", todo.index, name="index"),
    path("search/", todo.search, name="search"),
    path("<int:todo_id>/delete/", todo.delete_todo, name="delete_todo"),
    path("<int:todo_id>/toggle/", todo.toggle_todo, name="toggle_todo"),
    path("<int:todo_id>/", todo.todo_detail, name="todo_detail"),
    path("<int:todo_id>/update/", todo.update_todo, name="update_todo"),
    path("add/", todo.add_todo, name="add_todo"),
    path("accounts/login/", auth.login_view, name="login"),
    path("accounts/register/", auth.register_view, name="register"),
    path("accounts/logout/", auth.logout_view, name="logout"),
    # ex: /todo/5/
]