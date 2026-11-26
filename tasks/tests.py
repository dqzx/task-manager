from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')
        self.task1 = Task.objects.create(owner=self.user1, title='Задача первого пользователя')
        self.task2 = Task.objects.create(owner=self.user2, title='Задача второго пользователя')

    def test_login_required(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('users:login'), response.url)

    def test_task_list_filtered_by_owner(self):
        self.client.login(username='user1', password='Password123!')
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача первого пользователя')
        self.assertNotContains(response, 'Задача второго пользователя')

    def test_task_create_sets_owner_automatically(self):
        self.client.login(username='user1', password='Password123!')
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'Новая задача',
            'description': 'Описание',
            'priority': 'high',
        })
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.get(title='Новая задача')
        self.assertEqual(new_task.owner, self.user1)

    def test_cannot_edit_other_user_task(self):
        self.client.login(username='user1', password='Password123!')
        url = reverse('tasks:task_edit', args=[self.task2.id])
        response = self.client.post(url, {'title': 'Взломано', 'priority': 'low'})
        self.assertEqual(response.status_code, 404)
        self.task2.refresh_from_db()
        self.assertEqual(self.task2.title, 'Задача второго пользователя')

    def test_cannot_delete_other_user_task(self):
        self.client.login(username='user1', password='Password123!')
        url = reverse('tasks:task_delete', args=[self.task2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task2.id).exists())

    def test_nonexistent_task_returns_404(self):
        self.client.login(username='user1', password='Password123!')
        response = self.client.get(reverse('tasks:task_edit', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_toggle_task_status(self):
        self.client.login(username='user1', password='Password123!')
        url = reverse('tasks:task_toggle', args=[self.task1.id])
        self.client.post(url)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.completed)

        self.client.post(url)
        self.task1.refresh_from_db()
        self.assertFalse(self.task1.completed)

    def test_delete_via_get_not_allowed(self):
        self.client.login(username='user1', password='Password123!')
        url = reverse('tasks:task_delete', args=[self.task1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Task.objects.filter(id=self.task1.id).exists())
