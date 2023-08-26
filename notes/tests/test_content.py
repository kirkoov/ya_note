from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
# from django.utils import timezone

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):
    HOME_URL = reverse('notes:list')
    NOTE_TEST_NUM = 10

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        # cls.reader = User.objects.create(username='Читатель Простой')
        all_notes = []
        for index in range(TestNotesPage.NOTE_TEST_NUM):
            note = Note(
                title=f'Заголовок заметки Льва Николаича {index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'-{index}_',
            )
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_note_count(self):
        self.client.force_login(TestNotesPage.author)
        response = self.client.get(TestNotesPage.HOME_URL)
        self.assertEqual(
            len(response.context['note_list']),
            TestNotesPage.NOTE_TEST_NUM
        )

    def test_note_order(self):
        self.client.force_login(TestNotesPage.author)
        response = self.client.get(TestNotesPage.HOME_URL)
        note_list = response.context['note_list']
        all_ids = [note.id for note in note_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)

    def test_authorized_client_has_add_edit_forms(self):
        self.client.force_login(TestNotesPage.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (Note.objects.all()[0].slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_authorized_client_has_del_form(self):
        self.client.force_login(self.author)
        response = self.client.get(
            reverse('notes:delete',
                    args=(Note.objects.all()[0].slug,))
        )
        self.assertIn(
            f'/delete/{Note.objects.all()[0].slug}/',
            str(response.context['request'])
        )
