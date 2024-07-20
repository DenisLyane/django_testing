from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client

import pytest
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def count_date_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def list_comments(news, author):
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def form_data_new():
    return {
        'text': 'Обновлённый комментарий',
    }
