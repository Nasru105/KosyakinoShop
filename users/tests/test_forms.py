from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import UserRegistrationForm, UserLoginForm, ProfileForm

User = get_user_model()


class UserRegistrationFormTests(TestCase):
    def test_registration_form_valid_data(self):
        form_data = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "username": "ivan123",
            "email": "ivan@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_registration_form_passwords_mismatch(self):
        form_data = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "username": "ivan123",
            "email": "ivan@example.com",
            "password1": "strongpassword123",
            "password2": "differentpassword",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_missing_fields(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("username", form.errors)


class UserLoginFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
        )

    def test_login_form_valid(self):
        form_data = {
            "username": "testuser",
            "password": "testpassword123",
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_form_invalid_password(self):
        form_data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
        )

    def get_test_image(self):
        file = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(255, 0, 0))
        image.save(file, format="PNG")
        file.seek(0)
        return SimpleUploadedFile("test.png", file.read(), content_type="image/png")

    def test_profile_form_valid(self):
        image = self.get_test_image()
        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "username": "testuser",
            "email": "updated@example.com",
        }
        form = ProfileForm(data=form_data, files={"image": image}, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_profile_form_missing_fields(self):
        form_data = {
            "first_name": "",
            "last_name": "",
            "username": "",
            "email": "",
        }
        form = ProfileForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("username", form.errors)
        self.assertIn("email", form.errors)
