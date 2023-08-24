from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # cls.client = Client()
        cls.author = User.objects.create(username='Лев Толстой')
        # cls.reader = User.objects.create(username='Читатель Простой')
        # cls.client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='Заголовок заметки Льва Николаича',
            text='Текст заметки Толстого Л.В.',
            author=cls.author,
        )

    # def test_home_page(self):
    #     url = reverse('notes:home')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_detail_page(self):
    #     url = reverse('notes:detail', args=(self.note.slug,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_non_note_page_avaiability(self):
        urls = (
            ('notes:home', None),
            # ('notes:detail', (self.note.slug,), HTTPStatus.FOUND),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
