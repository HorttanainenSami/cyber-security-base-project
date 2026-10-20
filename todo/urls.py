from django.contrib import admin
from django.urls import path

from todo import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("<int:todo_id>/delete/", views.delete_todo, name="delete_todo"),
    path("<int:todo_id>/toggle/", views.toggle_todo, name="toggle_todo"),
    path("add/", views.add_todo, name="add_todo"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/register/", views.register_view, name="register"),
    path("accounts/logout/", views.logout_view, name="logout"),
    # ex: /todo/5/
]