import random
from http import HTTPStatus

from django.urls import reverse

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_create_comment(
    author,
    author_client,
    client,
    form_data,
    news,
    id_for_args
):
    url = reverse('news:detail', args=(id_for_args))
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 0

    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{url}#comments')

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, id_for_args):
    url = reverse('news:detail', args=(id_for_args))
    bad_words_data = {
        'text': f'Какой-то текст, {random.choice(BAD_WORDS)}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assertFormError(response, 'form', 'text', errors=WARNING)

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_author_can_delete_comment(author_client, comment, id_for_args):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    url_to_comments = reverse('news:detail', args=(id_for_args)) + '#comments'
    assertRedirects(response, url_to_comments)

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND)
    ),
)
def test_anonymous_and_user_cant_delete_comment_of_another_user(
    parametrized_client,
    comment,
    expected_status
):
    url = reverse('news:delete', args=(comment.id,))
    response = parametrized_client.delete(url)
    assert response.status_code == expected_status

    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_author_can_edit_comment(
    author_client,
    comment,
    id_for_args,
    form_data
):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    url_to_comments = reverse('news:detail', args=(id_for_args)) + '#comments'
    assertRedirects(response, url_to_comments)

    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND)
    ),
)
def test_anonymous_and_user_cant_edit_comment_of_another_user(
    comment,
    form_data,
    parametrized_client,
    expected_status
):
    url = reverse('news:edit', args=(comment.id,))
    response = parametrized_client.post(url, data=form_data)
    assert response.status_code == expected_status
    comment.refresh_from_db()
    assert comment.text == comment.text
