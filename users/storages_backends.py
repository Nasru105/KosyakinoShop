from storages.backends.s3boto3 import S3Boto3Storage

from app.settings import AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME


class UserImageStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    endpoint_url = AWS_S3_ENDPOINT_URL
    file_overwrite = False
    custom_domain = f"storage.yandexcloud.net/{bucket_name}"

    def image_path(instance, filename):
        """
        Генерирует путь для загрузки изображений пользователей.
        """
        username = instance.username.replace(" ", "_").lower() if instance.username else "unknown_user"
        return f"users_images/{username}/{filename}"
