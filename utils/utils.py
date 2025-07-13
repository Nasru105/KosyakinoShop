def get_all_fields(model, ordered_fields):

    def flatten(items):
        result = []
        for item in items:
            if isinstance(item, (list, tuple)):
                result.extend(flatten(item))
            else:
                result.append(item)
        return result

    # Получаем список всех полей модели User
    fields = [field.name for field in model._meta.get_fields() if not field.many_to_many and not field.one_to_many]
    fields.remove("id")  # Удаляем поле id, если оно есть

    for f in flatten(ordered_fields):
        if f in fields:
            fields.remove(f)
    fields = ordered_fields + fields

    return fields


def phone_number_format(phone_number: str):
    """Функция для форматирования номера телефона."""
    if not phone_number:
        return ""
    # Убираем плюс, пробелы, дефисы
    phone_number = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    # Если начинается с 8 или 7, убираем первый символ (код страны)
    if phone_number.startswith("8") or phone_number.startswith("7") or phone_number.startswith("+7"):
        phone_number = phone_number[1:]
    if len(phone_number) == 10:
        return f"({phone_number[:3]}) {phone_number[3:6]}-{phone_number[6:8]}-{phone_number[8:]}"
    return phone_number


def product_image_path(instance, filename):
    """
    Генерирует путь для загрузки изображений продуктов.
    Подходит для Products и ProductImage.
    """
    product_name = "unknown"

    if hasattr(instance, "name") and instance.name:
        product_name = instance.name.replace(" ", "_").lower()
    elif hasattr(instance, "product") and instance.product and hasattr(instance.product, "name"):
        product_name = instance.product.name.replace(" ", "_").lower()

    return f"goods_images/{product_name}/{filename}"


def user_image_path(instance, filename):
    """
    Генерирует путь для загрузки изображений пользователей.
    """
    username = instance.username.replace(" ", "_").lower() if instance.username else "unknown_user"
    return f"users_images/{username}/{filename}"
