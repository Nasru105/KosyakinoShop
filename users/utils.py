from django.db.models import F, ExpressionWrapper, FloatField, Prefetch, Sum
from carts.models import Cart
from orders.models import Order, OrderItem


def get_user_carts(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).order_by("id").select_related("product_variant")

    if not request.session.session_key:
        request.session.create()
    return Cart.objects.filter(session_key=request.session.session_key).order_by("id").select_related("product_variant")


def get_user_orders(request):
    if request.user.is_authenticated:
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related(Prefetch("orderitem_set", queryset=OrderItem.objects.select_related("product_variant")))
            .annotate(
                total_sum=Sum(
                    ExpressionWrapper(F("orderitem__price") * F("orderitem__quantity"), output_field=FloatField())
                )
            )
            .order_by("-id")
        )

    return orders
