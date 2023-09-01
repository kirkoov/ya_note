from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст новой заметки'
    NOTE_TITLE = 'NewNote'
    NOTE_TEXT_UPD = 'Текст заметки UPDATED'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель Простой')
        cls.note = Note.objects.create(
            title='Заголовок заметки Льва Николаича',
            text='Текст заметки Толстого Л.Н.',
            author=cls.author,
        )
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.reader_client = Client()
        cls.auth_client.force_login(cls.author)
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

    def test_auth_user_cant_use_same_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.form_data["title"].lower() + WARNING}'
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)  # There're only two test notes so far

    def test_author_can_delete_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.all()[1]  # Picking up the second note
        response = self.auth_client.delete(
            reverse('notes:delete', args=((note.slug,)))
        )
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)  # There's only one left

    def test_user_cant_delete_note_of_another_user(self):
        self.reader_client.force_login(self.reader)
        response = self.reader_client.delete(
            reverse('notes:delete', args=((self.note.slug,))))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        self.form_data['text'] = self.NOTE_TEXT_UPD
        response = self.auth_client.post(
            reverse('notes:edit', args=((self.note.slug,))),
            data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_UPD)

    def test_user_cant_edit_comment_of_another_user(self):
        self.form_data['text'] = self.NOTE_TEXT_UPD
        response = self.reader_client.post(
            reverse('notes:edit', args=((self.note.slug,))),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TestNoteCreation.note.text)
