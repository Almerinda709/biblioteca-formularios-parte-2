from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Author, Book, Category


class AuthorTests(TestCase):
    def test_nacionalidade_e_opcional(self):
        autor = Author.objects.create(name="Machado de Assis")
        self.assertEqual(autor.nationality, "")

    def test_autor_com_livros_nao_pode_ser_apagado(self):
        autor = Author.objects.create(name="Machado de Assis")
        Book.objects.create(title="Dom Casmurro", author=autor, year=1899)
        with self.assertRaises(ProtectedError):
            autor.delete()

    def test_autor_sem_livros_pode_ser_apagado(self):
        autor = Author.objects.create(name="Jorge Amado")
        autor.delete()
        self.assertEqual(Author.objects.count(), 0)

    def test_related_name_books(self):
        autor = Author.objects.create(name="Machado de Assis")
        Book.objects.create(title="Dom Casmurro", author=autor, year=1899)
        Book.objects.create(title="Quincas Borba", author=autor, year=1891)
        self.assertEqual(autor.books.count(), 2)

    def test_autores_ordenados_por_nome(self):
        Author.objects.create(name="Jorge Amado")
        Author.objects.create(name="Clarice Lispector")
        nomes = [a.name for a in Author.objects.all()]
        self.assertEqual(nomes, ["Clarice Lispector", "Jorge Amado"])


class CategoryTests(TestCase):
    def test_nome_unico(self):
        Category.objects.create(name="Romance")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Romance")


class BookTests(TestCase):
    def test_livro_pode_ficar_sem_categoria(self):
        autor = Author.objects.create(name="Machado de Assis")
        livro = Book.objects.create(title="Dom Casmurro", author=autor, year=1899)
        self.assertEqual(livro.categories.count(), 0)

    def test_livro_com_varias_categorias(self):
        autor = Author.objects.create(name="Machado de Assis")
        livro = Book.objects.create(title="Dom Casmurro", author=autor, year=1899)
        livro.categories.set([Category.objects.create(name="Romance"), Category.objects.create(name="Clássico")])
        self.assertEqual(livro.categories.count(), 2)


class NovoAutorTests(TestCase):
    def test_pagina_abre_com_formulario(self):
        resposta = self.client.get(reverse("biblioteca:novo_autor"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "csrfmiddlewaretoken")
        self.assertContains(resposta, "Nacionalidade")

    def test_cadastra_e_redireciona_para_o_autor(self):
        resposta = self.client.post(
            reverse("biblioteca:novo_autor"),
            {"nome": "Clarice Lispector", "nacionalidade": "Brasileira"},
        )
        autor = Author.objects.get()
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[autor.pk]))
        self.assertEqual(autor.nationality, "Brasileira")

    def test_nacionalidade_pode_ficar_em_branco(self):
        self.client.post(reverse("biblioteca:novo_autor"), {"nome": "Jorge Amado", "nacionalidade": ""})
        self.assertEqual(Author.objects.get().nationality, "")

    def test_sem_nome_mostra_erro_e_nao_salva(self):
        resposta = self.client.post(reverse("biblioteca:novo_autor"), {"nome": "", "nacionalidade": "Brasileira"})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Informe o nome do autor.")
        self.assertEqual(Author.objects.count(), 0)

    def test_post_sem_csrf_e_bloqueado(self):
        cliente = Client(enforce_csrf_checks=True)
        resposta = cliente.post(reverse("biblioteca:novo_autor"), {"nome": "Jorge Amado"})
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(Author.objects.count(), 0)

    def test_lista_tem_link_novo_autor(self):
        resposta = self.client.get(reverse("biblioteca:listar_livros"))
        self.assertContains(resposta, reverse("biblioteca:novo_autor"))
