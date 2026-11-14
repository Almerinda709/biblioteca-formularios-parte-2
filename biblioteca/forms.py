from django import forms


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
