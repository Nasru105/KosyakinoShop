from io import BytesIO
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from carts.models import Cart

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "StrongPass123"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )
        self.login_url = reverse("user:login")
        self.registration_url = reverse("user:registration")
        self.profile_url = reverse("user:profile")
        self.logout_url = reverse("user:logout")
        self.index_url = reverse("main:index")

    def get_test_image(self):
        file = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(255, 0, 0))
        image.save(file, format="PNG")
        file.seek(0)
        return SimpleUploadedFile("test.png", file.read(), content_type="image/png")

    def test_login_view_get(self):
        """Проверяем, что login view открывается"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertIn("title", response.context)
        self.assertEqual(response.context["title"], "Kosyakino - Авторизация")

    def test_login_view_success(self):
        """Проверяем успешный логин"""
        session_key = self.client.session.session_key
        response = self.client.post(self.login_url, {"username": self.user.username, "password": self.password})
        self.assertRedirects(response, self.index_url)
        # пользователь должен быть авторизован
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_view_with_next(self):
        """Проверка редиректа с параметром next"""
        next_page = reverse("user:profile")
        response = self.client.post(
            self.login_url, {"username": self.user.username, "password": self.password, "next": next_page}
        )
        self.assertRedirects(response, next_page)

    def test_registration_view_get(self):
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/registration.html")
        self.assertIn("title", response.context)
        self.assertEqual(response.context["title"], "Kosyakino - Регистрация")

    def test_registration_success(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Newpass123!",
            "password2": "Newpass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(self.registration_url, data)
        self.assertRedirects(response, self.profile_url)
        user = User.objects.get(username="newuser")
        self.assertTrue(user)
        # Проверяем, что пользователь авторизован сразу после регистрации
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        # должен редиректить на логин
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("user:login"), response.url)

    def test_profile_view_loads_for_authenticated_user(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIn("title", response.context)
        self.assertEqual(response.context["title"], "Kosyakino - Профиль")

    def test_profile_update(self):
        self.client.login(username=self.user.username, password=self.password)
        # Пошлем апдейт формы профиля
        response = self.client.post(
            self.profile_url,
            {"username": "updatedname", "email": "updated@example.com", "first_name": "Updated", "last_name": "User"},
        )
        self.assertRedirects(response, self.profile_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updatedname")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_logout_view(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.index_url)
        # После логаута пользователь должен быть анонимным
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("user:login"), response.url)

    def test_profile_image_upload(self):
        """Проверяем загрузку аватарки на странице профиля"""
        self.client.login(username=self.user.username, password=self.password)
        image_data = self.get_test_image()
        data = {
            "username": self.user.username,
            "email": self.user.email,
            "image": image_data,
            "first_name": "TestFirst",
            "last_name": "TestLast",
        }
        response = self.client.post(self.profile_url, data, files={"image": image_data})
        self.assertEqual(response.status_code, 302)
        # Обновляем пользователя из базы
        self.user.refresh_from_db()
        self.assertTrue(self.user.image)
