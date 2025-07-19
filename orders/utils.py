from django.core.mail import send_mail
from app import settings
from utils.utils import phone_number_format


def send_order_email(order, order_items):
    subject = f"Новый заказ №{order.display_id()}"

    # Товары в HTML
    html_items = ""
    for item in order_items:
        html_items += f'<li><a href="{item.product_link()} class="text-dark"">{item.name} {item.product_variant.sku}</a> — {item.quantity} шт. * {item.price} ₽</li>'

    html_message = f"""
        <p><strong>Пользователь:</strong> {order.user.get_full_name()} ({order.user.username})</p>
        <p><strong>Email:</strong> {order.user.email}</p>
        <p><strong>Телефон:</strong> +7 {phone_number_format(order.phone_number)}</p>
        <p><strong>Адрес доставки:</strong> {order.delivery_address}</p>
        <p><strong>Комментарий:</strong> {order.comment}</p>
        <p><strong>Товары:</strong></p>
        <ul>
            {html_items}
        </ul>
        <p><strong>Итого:</strong> {order.total_price()} ₽</p>
    """

    # Письмо в текстовом формате (на всякий случай)
    text_message = (
        f"Пользователь: {order.user.get_full_name()} ({order.user.username})\n"
        f"Email: {order.user.email}\n"
        f"Телефон: +7 {phone_number_format(order.phone_number)}\n"
        f"Адрес доставки: {order.delivery_address}\n"
        f"Комментарий: {order.comment}\n"
        f"Товары:\n"
    )
    for item in order_items:
        text_message += f"- {item.name} ({item.product_link()}) — {item.quantity} шт.\n"

    text_message += f"\nИтого: {order.total_price()} ₽"

    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=settings.ADMINS_EMAILS,
        html_message=html_message,
        fail_silently=False,
    )
