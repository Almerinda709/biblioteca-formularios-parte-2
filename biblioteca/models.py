from django.db import models
from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
)
from .validators import validar_ano_publicacao


class Author(models.Model):
    name = models.CharField(max_length=120)
    nationality = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(
        "título",
        max_length=200,
        validators=[MinLengthValidator(3)]
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="autor",
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="books",
        verbose_name="categorias",
    )

    year = models.IntegerField(
        "ano de publicação",
        validators=[
            MinValueValidator(1450),
            validar_ano_publicacao,
        ]
    )

    available = models.BooleanField("disponível", default=True)

    pages = models.PositiveIntegerField(
        "páginas",
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5000),
        ]
    )

    isbn = models.CharField(
        "ISBN",
        max_length=13,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{13}$",
                message="O ISBN deve possuir exatamente 13 dígitos."
            )
        ]
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

    def __str__(self):
        return f"{self.title} ({self.year})"

