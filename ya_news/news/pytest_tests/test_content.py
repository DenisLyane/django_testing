from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

import pytest
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, count_date_news):
    response = count_date_news
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert list(object_list) == sorted(
        object_list,
        key=lambda news: news.date,
        reverse=True
    )


@pytest.mark.django_db
@pytest.mark.usefixtures('list_comments')
def test_comments_order(client, id_for_args):
    url = reverse('news:detail', args=(id_for_args))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, author_client, id_for_args):
    url = reverse('news:detail', args=(id_for_args))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context

    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
