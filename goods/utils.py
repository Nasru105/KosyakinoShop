from re import search
from goods.models import Product
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchHeadline,  # type: ignore
    SearchVector,
    SearchRank,
    SearchQuery,
)


def q_search(query):

    vector = SearchVector("name") + SearchVector("description") + SearchVector("sku") + SearchVector("firm")
    # query = SearchQuery(query, config="russian")  # Указываем язык для морфологии

    goods = Product.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0.00001).order_by("-rank")

    goods = goods.annotate(
        headline=SearchHeadline(
            "name",
            query,
            start_sel="<span style='background-color: yellow;'>",
            stop_sel="</span>",
        )
    )

    goods = goods.annotate(
        bodyline=SearchHeadline(
            "description",
            query,
            start_sel="<span style='background-color: yellow;'>",
            stop_sel="</span>",
        )
    )
    return goods

    # keywords = [word for word in query.split() if len(word) > 2]
    # q_objects = Q()

    # for token in keywords:
    #     q_objects |= Q(description__icontains=token)
    #     q_objects |= Q(name__icontains=token)

    # return Product.objects.filter(q_objects)
