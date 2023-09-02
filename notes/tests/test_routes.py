from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    REPEATED_URLS = ('notes:edit', 'notes:delete')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель Простой')
        cls.note = Note.objects.create(
            title='Заголовок заметки Льва Николаича',
            text='Текст заметки Толстого Л.Н.',
            author=cls.author,
        )

    def sub_test_em(self, urls, client, status):
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = client.get(url)
                return self.assertEqual(response.status_code, status)

    def check_author_reader_for_200(self, urls):
        for another in TestRoutes.author, TestRoutes.reader:
            self.client.force_login(another)
            self.sub_test_em(urls, self.client, HTTPStatus.OK)

    # Главная страница доступна анонимному пользователю.
    # +Страницы регистрации пользователей, входа в учётную запись и выхода из
    # неё доступны всем пользователям.
    def test_page_avaiability_for_all_users(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        self.sub_test_em(urls, self.client, HTTPStatus.OK)
        self.check_author_reader_for_200(urls)

    # Аутентифицированному пользователю доступна страница со списком заметок
    # notes/, страница успешного добавления заметки done/, страница добавления
    # новой заметки add/.
    def test_page_avaiability_for_auth_user(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        self.check_author_reader_for_200(urls)

    # Страницы отдельной заметки, удаления и редактирования заметки доступны
    # только автору заметки. Если на эти страницы попытается зайти другой
    # пользователь, вернётся ошибка 404.
    def test_page_avaiability_for_note_author_only(self):
        urls = (
            ('notes:detail', (TestRoutes.note.slug,)),
            ('notes:delete', (TestRoutes.note.slug,)),
            ('notes:edit', (TestRoutes.note.slug,)),
        )
        self.client.force_login(TestRoutes.author)
        self.sub_test_em(urls, self.client, HTTPStatus.OK)
        self.client.force_login(TestRoutes.reader)
        self.sub_test_em(urls, self.client, HTTPStatus.NOT_FOUND)

    # При попытке перейти на страницу списка заметок, страницу успешного
    # добавления записи, страницу добавления заметки, отдельной заметки,
    # редактирования или удаления заметки анонимный пользователь
    # перенаправляется на страницу логина.
    def test_page_avaiability_for_anon_user(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (TestRoutes.note.slug,)),
            ('notes:add', None),
            ('notes:delete', (TestRoutes.note.slug,)),
            ('notes:edit', (TestRoutes.note.slug,)),
        )
        login_url = reverse('users:login')
        for url, args in urls:
            with self.subTest(url=url):
                url_ = reverse(url, args=args)
                redirect_url = f'{login_url}?next={url_}'
                response = self.client.get(url_)
                self.assertRedirects(response, redirect_url)
