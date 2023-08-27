# from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

# from news.forms import BAD_WORDS, WARNING
from notes.models import Note


User = get_user_model()

# 1. Анонимный пользователь не может оставить заметку.
# 2. Авторизованный пользователь может оставить заметку.
# 3. Авторизованный пользователь может редактировать или удалять свои заметки.
# 5. Авторизованный пользователь не может редактировать или удалять чужие заметки.


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст новой заметки'
    NOTE_TITLE = 'NewNote'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель Простой')
        cls.note = Note.objects.create(
            title='Заголовок заметки Льва Николаича',
            text='Текст заметки Толстого Л.Н.',
            author=cls.author,
        )

        # Адрес создания заметки.
        # cls.url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url = reverse('notes:add')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        # Данные для POST-запроса при создании заметки.
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.author,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)  # One is initially there for testing

    def test_auth_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        note = Note.objects.all()[1]  # Picking up the second note
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.author)
