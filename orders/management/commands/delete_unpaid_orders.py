from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order


class Command(BaseCommand):
    help = "Удаляет неоплаченные заказы старше 72 часов"

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timezone.timedelta(hours=72)

        orders = Order.objects.filter(status=Order.STATUS_PENDING, created_timestamp__lt=threshold)

        count = orders.count()
        orders.delete()

        self.stdout.write(self.style.SUCCESS(f"Удалено {count} неоплаченных заказов."))
