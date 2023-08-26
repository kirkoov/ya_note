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

#     def test_news_order(self):
#         response = self.client.get(self.HOME_URL)
#         news_list = response.context['news_list']
#         all_dates = [news.date for news in news_list]
#         # Сортируем полученный список по убыванию.
#         sorted_dates = sorted(all_dates, reverse=True)
#         # Проверяем, что исходный список был отсортирован правильно.
#         self.assertEqual(all_dates, sorted_dates)


# class TestDetailPage(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(
#             title='Тестовая новость', text='Просто текст.'
#         )
#         cls.detail_url = reverse('news:detail', args=(cls.news.id,))
#         cls.author = User.objects.create(username='Комментатор')
#         now = timezone.now()
#         for index in range(2):
#             comment = Comment.objects.create(
#                 news=cls.news, author=cls.author, text=f'Tекст {index}',
#             )
#             comment.created = now + timedelta(days=index)
#             comment.save()

#     def test_comments_order(self):
#         response = self.client.get(self.detail_url)
#         # Проверяем, что объект новости находится в словаре контекста
#         # под ожидаемым именем - названием модели.
#         self.assertIn('news', response.context)
#         # Получаем объект новости.
#         news = response.context['news']
#         # Получаем все комментарии к новости.
#         all_comments = news.comment_set.all()
#         # Проверяем, что время создания первого комментария в списке
#         # меньше, чем время создания второго.
#         self.assertLess(all_comments[0].created, all_comments[1].created)

#     def test_anonymous_client_has_no_form(self):
#         response = self.client.get(self.detail_url)
#         self.assertNotIn('form', response.context)

#     def test_authorized_client_has_form(self):
#         # Авторизуем клиент при помощи ранее созданного пользователя.
#         self.client.force_login(self.author)
#         response = self.client.get(self.detail_url)
#         self.assertIn('form', response.context)
