from http import HTTPStatus

from pytils.translit import slugify  # type: ignore[import]

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNotesLogic(TestCase):
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
        cls.add_url = reverse('notes:add')
        cls.auth_client = Client()
        cls.reader_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.author,
            'slug': 'LuKkY',
        }

    # Залогиненный пользователь может создать заметку, а анонимный — не может.
    def test_auth_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.author)

    def test_anon_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    # Невозможно создать две заметки с одинаковым slug.
    def test_auth_user_cant_use_same_slug(self):
        self.auth_client.post(self.add_url, data=self.form_data)
        self.reader_client.force_login(self.reader)
        new_form_data = {
            'title': 'Another title',
            'text': 'Another text',
            'author': self.reader_client,
            'slug': self.form_data['slug'],
        }
        client_calls = (
            self.reader_client.post(self.add_url, data=new_form_data),
            self.auth_client.post(self.add_url, data=new_form_data),
        )
        for client_call in client_calls:
            with self.subTest(name=client_call):
                self.assertFormError(
                    client_call,
                    form='form',
                    field='slug',
                    errors=f'{new_form_data["slug"] + WARNING}'
                )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)  # There're two test notes initially

    # Если при создании заметки не заполнен slug, то он формируется
    # автоматически, с помощью функции pytils.translit.slugify.
    def test_slugify_with_no_slug_note(self):
        default_slug = slugify(TestNotesLogic.note.title)
        self.assertEqual(
            default_slug,
            TestNotesLogic.note.slug
        )
        test_note_with_no_slug = Note.objects.get(slug=default_slug)
        self.assertIsInstance(test_note_with_no_slug, Note)

    # Пользователь может редактировать и удалять свои заметки, но не может
    # редактировать или удалять чужие.
    def test_author_can_edit_delete_note(self):
        edit_url = reverse('notes:edit', args=((self.note.slug,)))
        del_url = reverse('notes:delete', args=((self.note.slug,)))
        ok_url = reverse('notes:success')
        self.form_data['text'] = self.NOTE_TEXT_UPD
        response = self.auth_client.post(edit_url, data=self.form_data)
        self.assertRedirects(response, ok_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_UPD)
        response = self.auth_client.delete(del_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)  # The initial test note of the Class

    def test_user_cant_delete_note_of_another_author(self):
        self.reader_client.force_login(self.reader)
        response = self.reader_client.delete(
            reverse('notes:delete', args=((self.note.slug,))))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_cant_edit_comment_of_another_author(self):
        self.form_data['text'] = self.NOTE_TEXT_UPD
        self.reader_client.force_login(self.reader)
        response = self.reader_client.post(
            reverse('notes:edit', args=((self.note.slug,))),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TestNotesLogic.note.text)
