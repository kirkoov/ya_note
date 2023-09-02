import pytest
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse


# В тесте используем фикстуру заметки и фикстуру клиента с автором заметки.
# def test_note_in_list_for_author(note, author_client):
#     url = reverse('notes:list')
#     response = author_client.get(url)
#     object_list = response.context['object_list']
#     assert note in object_list


# # В этом тесте тоже используем фикстуру заметки,
# # но в качестве клиента используем admin_client;
# # он не автор заметки, так что заметка не должна быть ему видна.
# def test_note_not_in_list_for_another_user(note, admin_client):
#     url = reverse('notes:list')
#     response = admin_client.get(url)
#     object_list = response.context['object_list']
#     # Проверяем, что заметки нет в контексте страницы:
#     assert note not in object_list


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (lazy_fixture('author_client'), True),
        (lazy_fixture('admin_client'), False),
    )
)
def test_notes_list_for_different_users(
        note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


# def test_create_note_page_contains_form(author_client):
#     url = reverse('notes:add')
#     response = author_client.get(url)
#     assert 'form' in response.context


# В параметры теста передаём фикстуру slug_for_args и клиент с автором заметки:
# def test_edit_note_page_contains_form(slug_for_args, author_client):
#     url = reverse('notes:edit', args=slug_for_args)
#     response = author_client.get(url)
#     assert 'form' in response.context


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
