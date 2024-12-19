from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task

class TaskViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.task = Task.objects.create(
            user=cls.user,
            title="Test Task",
            description="Test Description",
            complete=False
        )

    def setUp(self):
        self.client.login(username='testuser', password='12345')

    def test_custom_login_view(self):
        self.client.logout()  # Выйти из системы перед проверкой
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)  # Статус должен быть 200 для неаутентифицированного пользователя
        self.assertTemplateUsed(response, 'base/login.html')


    def test_register_page_view(self):
        self.client.logout()  # Выйти из системы перед проверкой
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)  # Статус должен быть 200 для неаутентифицированного пользователя
        self.assertTemplateUsed(response, 'base/register.html')

    def test_redirect_authenticated_user_from_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)  # Проверяем редирект
        self.assertRedirects(response, reverse('tasks'))  # Проверяем, что редирект ведёт на 'tasks'


    def test_task_list_view(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/task_list.html')
        self.assertContains(response, "Test Task")


    def test_task_create_view(self):
        response = self.client.post(reverse('task-create'), {
            'title': 'New Task',
            'description': 'New Description',
            'complete': False
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_task_update_view(self):
        response = self.client.post(reverse('task-update', args=[self.task.id]), {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'complete': True
        })
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertTrue(self.task.complete)

    def test_task_delete_view(self):
        response = self.client.post(reverse('task-delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_task_reorder_view(self):
        task2 = Task.objects.create(user=self.user, title="Second Task")
        position_data = {"position": f"{task2.id},{self.task.id}"}
        response = self.client.post(reverse('task-reorder'), position_data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(list(self.user.task_set.values_list('id', flat=True)), [task2.id, self.task.id])
