def get_fields(model, ordered_fields):
    # Получаем список всех полей модели User
    fields = [field.name for field in model._meta.get_fields() if not field.many_to_many and not field.one_to_many]
    fields.remove("id")  # Удаляем поле id, если оно есть
    # Если хочешь поля в конкретном порядке, например username и email впереди:
    for f in ordered_fields:
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
    if phone_number.startswith("8") or phone_number.startswith("7"):
        phone_number = phone_number[1:]
        if len(phone_number) == 10:
            return f"({phone_number[:3]}) {phone_number[3:6]}-{phone_number[6:8]}-{phone_number[8:]}"
    return phone_number
