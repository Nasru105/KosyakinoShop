from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="test@example.com", phone_number="1234567890"
        )

    def test_user_str_returns_username(self):
        self.assertEqual(str(self.user), "testuser")

    def test_user_has_phone_number(self):
        self.assertEqual(self.user.phone_number, "1234567890")

    def test_user_image_upload(self):
        # создаем фиктивный файл-аватар
        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
        image_file = SimpleUploadedFile(name="test_image.gif", content=image_content, content_type="image/gif")
        user_with_image = User.objects.create_user(username="imageuser", password="password123", image=image_file)
        self.assertTrue(user_with_image.image.name.startswith("users_images/"))
        self.assertTrue(user_with_image.image.name.startswith("users_images/"))
        self.assertTrue(user_with_image.image.name.endswith(".gif"))
