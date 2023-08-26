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
            text='Текст заметки Толстого Л.В.',
            author=cls.author,
        )

    def test_non_note_page_avaiability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        self.sub_test_em(urls, HTTPStatus.OK)

    def test_detail_add_pages(self):
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:add', None),
        )
        self.sub_test_em(urls, HTTPStatus.FOUND)

    def test_note_list_page(self):
        url = reverse('notes:list')
        self.client.force_login(TestRoutes.author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (TestRoutes.author, HTTPStatus.OK),
            (TestRoutes.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in TestRoutes.REPEATED_URLS:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in TestRoutes.REPEATED_URLS:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def sub_test_em(self, urls, status):
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                return self.assertEqual(response.status_code, status)
