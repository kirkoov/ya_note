from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Mimo Pro][odil')
        all_notes_byLeo = []
        for index in range(3):
            note = Note(
                title=f'Заголовок заметки Льва Николаича {index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'-{index}_',
            )
            all_notes_byLeo.append(note)
        Note.objects.bulk_create(all_notes_byLeo)

        all_notes_byMimo = []
        for index in range(5):
            note = Note(
                title=f'Заголовок заметки Mimo {index}',
                text='Simply текст.',
                author=cls.reader,
                slug=f'm{index}O',
            )
            all_notes_byMimo.append(note)
        Note.objects.bulk_create(all_notes_byMimo)

    def get_auth_user_note_list(self, user):
        notes_url = reverse('notes:list')
        self.client.force_login(user)
        response = self.client.get(notes_url)
        return response.context['note_list']

    def test_note_in_list_for_author(self):
        # Отдельная заметка передаётся на страницу со списком заметок в списке
        # object_list в словаре context.
        # _url = reverse('news:detail', args=(news.id,))
        note_list = self.get_auth_user_note_list(TestNotesPage.author)
        note_count_ini = len(note_list)
        new_note_form_data = {
            'title': 'Заголовок новой заметки Leo',
            'text': 'Текст новой заметки.',
            'author': TestNotesPage.author,
            'slug': 'test_sluGgish',
        }
        add_note_url = reverse('notes:add')
        self.client.post(add_note_url, data=new_note_form_data)
        object_list = self.get_auth_user_note_list(TestNotesPage.author)
        new_note_in_there = False
        for note in object_list:
            if new_note_form_data['slug'] == note.slug:
                new_note_in_there = True
                break
        self.assertTrue(new_note_in_there)
        note_count_now = len(object_list)
        self.assertEqual(note_count_now, note_count_ini + 1)

    def test_note_lists_differ_for_diff_authors(self):
        # В список заметок одного пользователя не попадают заметки другого.
        note_list_leo = self.get_auth_user_note_list(TestNotesPage.author)
        note_list_mimo = self.get_auth_user_note_list(TestNotesPage.reader)
        self.assertNotEqual(note_list_leo, note_list_mimo)

    def test_add_edit_pages_have_forms(self):
        # На страницы создания и редактирования заметки передаются формы.
        # (для авторизованных пользователей, с заметками)
        note = Note.objects.create(
            title='Заголовок test-заметки Mimo',
            text='Simply a test note by Mimo.',
            author=TestNotesPage.reader,
            slug='1test-note_slu9',
        )
        self.client.force_login(TestNotesPage.reader)
        add_edit_urls = (
            ('notes:add', None),
            ('notes:edit', (note.slug,)),
        )
        for name, args in add_edit_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
