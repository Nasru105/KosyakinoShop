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
