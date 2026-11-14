from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import Client, TestCase
from django.utils import timezone
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


class LivroFormTests(TestCase):
    def setUp(self):
        self.autor = Author.objects.create(name="Machado de Assis")
        self.romance = Category.objects.create(name="Romance")
        self.classico = Category.objects.create(name="Clássico")
        self.livro = Book.objects.create(title="Dom Casmurro", author=self.autor, year=1899)
        self.livro.categories.add(self.romance)

    def dados(self, **extra):
        dados = {"title": "Quincas Borba", "author": self.autor.pk, "year": 1891, "available": "on"}
        dados.update(extra)
        return dados

    def test_novo_livro_abre_vazio(self):
        resposta = self.client.get(reverse("biblioteca:novo_livro"))
        self.assertContains(resposta, "<title>Novo livro</title>", html=False)
        self.assertContains(resposta, "Cadastrar livro")
        self.assertContains(resposta, 'type="checkbox" name="categories"')

    def test_cria_livro_sem_categoria_e_volta_pro_autor(self):
        resposta = self.client.post(reverse("biblioteca:novo_livro"), self.dados())
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        novo = Book.objects.get(title="Quincas Borba")
        self.assertEqual(novo.categories.count(), 0)

    def test_cria_livro_com_categorias(self):
        self.client.post(reverse("biblioteca:novo_livro"), self.dados(categories=[self.romance.pk, self.classico.pk]))
        self.assertEqual(Book.objects.get(title="Quincas Borba").categories.count(), 2)

    def test_editar_abre_preenchido(self):
        resposta = self.client.get(reverse("biblioteca:editar_livro", args=[self.livro.pk]))
        self.assertContains(resposta, "<title>Editar livro</title>", html=False)
        self.assertContains(resposta, "Salvar alterações")
        self.assertContains(resposta, 'value="Dom Casmurro"')
        self.assertContains(resposta, 'value="1899"')

    def test_editar_altera_o_mesmo_livro(self):
        outro = Author.objects.create(name="Clarice Lispector")
        resposta = self.client.post(
            reverse("biblioteca:editar_livro", args=[self.livro.pk]),
            self.dados(title="Dom Casmurro", author=outro.pk, year=1900),
        )
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[outro.pk]))
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.author, outro)
        self.assertEqual(self.livro.categories.count(), 0)
        self.assertEqual(Book.objects.count(), 1)

    def test_editar_livro_inexistente_da_404(self):
        resposta = self.client.get(reverse("biblioteca:editar_livro", args=[999]))
        self.assertEqual(resposta.status_code, 404)

    def test_titulo_tem_espacos_limpos(self):
        self.client.post(reverse("biblioteca:novo_livro"), self.dados(title="   Memorias    Postumas  de   Bras  "))
        self.assertTrue(Book.objects.filter(title="Memorias Postumas de Bras").exists())

    def test_titulo_curto_mostra_erro(self):
        resposta = self.client.post(reverse("biblioteca:novo_livro"), self.dados(title="   ab   "))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "pelo menos 3 caracteres")
        self.assertEqual(Book.objects.count(), 1)

    def test_ano_atual_e_aceito(self):
        ano = timezone.localdate().year
        self.client.post(reverse("biblioteca:novo_livro"), self.dados(year=ano))
        self.assertTrue(Book.objects.filter(year=ano).exists())

    def test_ano_no_futuro_mostra_erro(self):
        ano = timezone.localdate().year + 1
        resposta = self.client.post(reverse("biblioteca:novo_livro"), self.dados(year=ano))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "não pode ser depois de")
        self.assertEqual(Book.objects.count(), 1)

    def test_links_de_editar_e_novo_livro(self):
        lista = self.client.get(reverse("biblioteca:listar_livros"))
        self.assertContains(lista, reverse("biblioteca:novo_livro"))
        self.assertContains(lista, reverse("biblioteca:editar_livro", args=[self.livro.pk]))
        pagina_autor = self.client.get(reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.assertContains(pagina_autor, reverse("biblioteca:editar_livro", args=[self.livro.pk]))
