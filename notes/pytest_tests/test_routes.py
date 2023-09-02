import pytest
from pytest_lazyfixture import lazy_fixture

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(admin_client, name):
    url = reverse(name)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


# def test_note_exists(note):
#     notes_count = Note.objects.count()
#     # Общее количество заметок в БД равно 1.
#     assert notes_count == 1
#     # Заголовок объекта, полученного при помощи фикстуры note,
#     # совпадает с тем, что указан в фикстуре.
#     assert note.title == 'Заголовок'


# @pytest.mark.django_db
# def test_empty_db():
#     notes_count = Note.objects.count()
#     # В пустой БД никаких заметок не будет:
#     assert notes_count == 0

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, note, expected_status
):
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    # Вторым параметром передаём note_object,
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, note_object',
    (
        ('notes:detail', lazy_fixture('note')),
        ('notes:edit', lazy_fixture('note')),
        ('notes:delete', lazy_fixture('note')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
def test_redirects(client, name, note_object):
    login_url = reverse('users:login')
    if note_object is not None:
        url = reverse(name, args=(note_object.slug,))
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
