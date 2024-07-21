from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):

    NOTE_TEXT = 'Текст заметки'
    TITLE = 'Заголовок'
    SLUG = 'Slug'

    def setUp(self):
        self.user = User.objects.create(username='Гость')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.url = reverse('notes:add', None)
        self.form_data = {
            'text': self.NOTE_TEXT,
            'slug': self.SLUG,
            'author': self.user,
            'title': self.TITLE
        }

        self.form_data_no_slug = {
            'text': self.NOTE_TEXT,
            'author': self.user,
            'title': self.TITLE
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.slug, self.SLUG)
        self.assertEqual(new_note.author, self.user)
        self.assertEqual(new_note.title, self.TITLE)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        response = self.auth_client.post(self.url, data=self.form_data_no_slug)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        new_note = Note.objects.get()
        expected_slug = slugify(new_note.title)
        self.assertEqual(new_note.slug, expected_slug)


class TestSlugUnic(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'Slug'

    def setUp(self):
        self.url = reverse('notes:add')
        self.user = User.objects.create(username='Гость')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.note = Note.objects.create(
            title=self.TITLE,
            text=self.TEXT,
            author=self.user,
            slug=self.SLUG
        )

        self.form_data = {
            'text': self.TEXT,
            'slug': self.SLUG,
            'author': self.user,
            'title': self.TITLE
        }

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'Slug_1'
    NEXT_TITLE = 'Заголовок второй'
    NEXT_TEXT = 'Заметка вторая'
    NEXT_SLUG = 'Slug_2'

    def setUp(self):
        self.author = User.objects.create(username='Автор')
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader = User.objects.create(username='Читатель')
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        self.url = reverse('notes:add')
        self.note = Note.objects.create(
            title=self.TITLE, text=self.TEXT,
            slug=self.SLUG,
            author=self.author
        )

        self.note_url = reverse('notes:detail', args=(self.note.slug,))
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.delete_url = reverse('notes:delete', args=(self.note.slug,))

        self.form_data = {
            'text': self.NEXT_TEXT,
            'slug': self.NEXT_SLUG,
            'author': self.author,
            'title': self.NEXT_TITLE
        }

    def test_author_can_delete_note(self):
        """Пользователь может удалить свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEXT_TEXT)
        self.assertEqual(self.note.slug, self.NEXT_SLUG)
        self.assertEqual(self.note.title, self.NEXT_TITLE)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может может редактировать чужие заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
        self.assertEqual(self.note.title, self.TITLE)
