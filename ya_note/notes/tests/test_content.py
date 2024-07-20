from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUp(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slug',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        parametrized_client = (
            (self.author, True),
            (self.reader, False)
        )
        for user, note_in_list in parametrized_client:
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            object_list = response.context['object_list']
            self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for url, args in urls:
            url = reverse(url, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
