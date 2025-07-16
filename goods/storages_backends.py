import re
from storages.backends.s3boto3 import S3Boto3Storage

from app.settings import AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME


class ProductImageStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    endpoint_url = AWS_S3_ENDPOINT_URL
    file_overwrite = False
    custom_domain = f"storage.yandexcloud.net/{bucket_name}"

    def image_path(instance, filename):
        """
        Генерирует путь для загрузки изображений продуктов.
        Подходит для Products и ProductImage.
        """
        product_name = "unknown"

        if hasattr(instance, "name") and instance.name:
            product_name = f"{re.sub(r'[- ]', '_', instance.slug.lower())}"
        elif hasattr(instance, "product") and instance.product and hasattr(instance.product, "name"):
            product_name = f"{re.sub(r'[- ]', '_', instance.product.slug.lower())}"

        return f"goods_images/{product_name}/{filename}"
