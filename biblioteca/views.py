from django.shortcuts import get_object_or_404, redirect, render

from .forms import AutorForm
from .models import Author, Book


def listar_livros(request):
    livros = Book.objects.select_related("author")
    return render(request, "biblioteca/lista_livros.html", {"livros": livros})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, "biblioteca/author_detail.html", {"author": author, "livros": author.books.all()})


def novo_autor(request):
    if request.method == "POST":
        form = AutorForm(request.POST)
        if form.is_valid():
            autor = Author.objects.create(
                name=form.cleaned_data["nome"],
                nationality=form.cleaned_data["nacionalidade"],
            )
            return redirect("biblioteca:author_detail", pk=autor.pk)
    else:
        form = AutorForm()
    return render(request, "biblioteca/novo_autor.html", {"form": form})
