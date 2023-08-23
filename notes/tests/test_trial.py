from django.contrib.auth import get_user_model
from django.test import TestCase  # Client,

from notes.models import Note


User = get_user_model()


class TestNote(TestCase):

    TITLE = 'Заголовок заметки'
    TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        # cls.user_client = Client()
        # cls.user = User.objects.create(username='testUser')
        # cls.user_client.force_login(cls.user)
        cls.author = User.objects.create(username='123 Толстой')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
        )

    # slug = models.SlugField(
    #     'Адрес для страницы с заметкой',
    #     max_length=100,
    #     unique=True,
    #     blank=True,
    #     help_text=('Укажите адрес для страницы заметки. Используйте только '
    #                'латиницу, цифры, дефисы и знаки подчёркивания')
    # )

    def test_successful_creation(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        self.assertEqual(self.note.title, self.TITLE)
