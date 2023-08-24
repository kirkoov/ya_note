from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        # cls.author = User.objects.create(username='Лев Толстой')
        # cls.reader = User.objects.create(username='Читатель Простой')
        # cls.client.force_login(cls.author)

        # cls.note = Note.objects.create(
        #     title='Заголовок заметки',
        #     text='Текст заметки',
        #     author=cls.author,
        # )

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_home_page_loggedin(self):
    #     url = reverse('notes:home')
    #     response = self.test_client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_detail_page_anonymous(self):
    #     url = reverse('notes:detail', args=(self.note.slug,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)

    # def test_detail_page_loggedin_author(self):
    #     url = reverse('notes:detail', args=(self.note.slug,))
    #     response = self.test_client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_detail_page_loggedin_noauthor(self):
    #     url = reverse('notes:detail', args=(self.note.slug,))
    #     response = self.test_client2.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
