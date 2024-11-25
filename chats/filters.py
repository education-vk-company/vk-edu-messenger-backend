import re
from urllib.parse import unquote

from django.db.models import Q
from rest_framework import filters


class SearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search = request.GET.get("search")

        if not search:
            return queryset

        try:
            search = unquote(search)
        except:
            return queryset

        search = search.split()

        is_private_query = Q()
        is_group_query = Q()

        for term in search:
            regex = re.escape(term)

            is_private_query &= Q(members__last_name__iregex=regex) | Q(
                members__first_name__iregex=regex
            )

            is_group_query &= Q(title__iregex=regex)

        queryset = (
            queryset.prefetch_related("members")
            .filter(
                (Q(is_private=True) & is_private_query)
                | (Q(is_private=False) & is_group_query)
            )
            .distinct()
        )

        return queryset.order_by("-updated_at")
