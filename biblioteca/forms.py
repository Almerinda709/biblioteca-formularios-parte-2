from django import forms
from django.utils import timezone

from .models import Book


class AutorForm(forms.Form):
    nome = forms.CharField(
        label="Nome",
        max_length=120,
        error_messages={
            "required": "Informe o nome do autor.",
            "max_length": "O nome pode ter no máximo 120 caracteres, abrevie se precisar.",
        },
    )
    nacionalidade = forms.CharField(
        label="Nacionalidade",
        max_length=60,
        required=False,
        error_messages={
            "max_length": "A nacionalidade pode ter no máximo 60 caracteres.",
        },
    )


class LivroForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [  "title",
                    "author",
                    "year",
                    "available",
                    "categories",
                    "pages",
                    "isbn", ]
        labels = {
            "title": "Título",
            "author": "Autor",
            "year": "Ano de publicação",
            "available": "Disponível para empréstimo",
            "categories": "Categorias",
            "pages": "Páginas",
            "isbn": "ISBN",
        }
        widgets = {
            "categories": forms.CheckboxSelectMultiple,
        }
        error_messages = {
            "title": {"required": "Informe o título do livro."},
            "author": {
                "required": "Escolha o autor do livro. Se ele não estiver na lista, cadastre o autor primeiro.",
                "invalid_choice": "Esse autor não existe mais, escolha outro da lista.",
            },
            "year": {
                "required": "Informe o ano de publicação.",
                "invalid": "Digite o ano só com números, por exemplo 1899.",
            },
        }

    
def clean_title(self):
    return self.cleaned_data["title"].strip()

