from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils.timezone import make_aware

import settings
from db.models import Ticket, Order, MovieSession


@transaction.atomic
def create_order(tickets: list[dict],
                 username: str,
                 date: Optional[datetime] = None) -> Order:
    user = get_user_model().objects.get(username=username)
    if isinstance(date, str):
        parsed = datetime.strptime(date, "%Y-%m-%d %H:%M")
    elif isinstance(date, datetime):
        parsed = date
    else:
        parsed = None
    if settings.USE_TZ and parsed:
        parsed = make_aware(parsed)

    order = Order.objects.create(user=user)
    if parsed:
        order.created_at = parsed
    for ticket in tickets:
        ms = MovieSession.objects.get(pk=ticket["movie_session"])
        Ticket.objects.create(movie_session=ms,
                              order=order,
                              row=ticket["row"],
                              seat=ticket["seat"])
    return order


def get_orders(username: Optional[str] = None) -> QuerySet[Order]:
    if username:
        return (Order.objects.filter(user__username=username)
                .order_by("-created_at"))
    else:
        return Order.objects.all()
