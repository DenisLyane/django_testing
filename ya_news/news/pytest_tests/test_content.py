from django.conf import settings
from django.urls import reverse

import pytest
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, count_date_news):
    response = count_date_news
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('list_comments')
def test_comments_order(client, id_for_args):
    url = reverse('news:detail', args=(id_for_args))
    response = client.get(url)
    assert 'news' in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, author_client, id_for_args):
    url = reverse('news:detail', args=(id_for_args))
    response = client.get(url)
    assert 'form' not in response.context

    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
