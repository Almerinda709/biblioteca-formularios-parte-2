from django.urls import path

from . import views

app_name = "biblioteca"

urlpatterns = [
    path("", views.listar_livros, name="listar_livros"),
    path("autores/novo/", views.novo_autor, name="novo_autor"),
    path("autores/<int:pk>/", views.author_detail, name="author_detail"),
]
