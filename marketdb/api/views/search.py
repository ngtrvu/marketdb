import logging

from django.db.models import F, Value
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from core.models.search_index import SearchIndex
from api.serializers.search import SearchItemSerializer
from django.contrib.postgres.search import SearchRank, SearchQuery


class SearchView(ListAPIView):
    serializer_class = SearchItemSerializer
    queryset = SearchIndex.objects.all()
    ordering = ('symbol',)

    def list(self, request, *args, **kwargs):
        keyword = request.GET.get('keyword')
        if not keyword:
            return Response(data={}, status=status.HTTP_200_OK)

        # Filter
        filter_queryset = self.filter_queryset(self.get_queryset())

        # Search
        query = SearchQuery(Value(keyword), config='simple')
        queryset = filter_queryset.annotate(rank=SearchRank(F('search_vector'), query, weights=[0.05, 0.1, 0.25, 1]))

        if ' ' in keyword:
            queryset = queryset.filter(search_vector=query).order_by('-rank')
        else:
            queryset = queryset.filter(search_vector__icontains=keyword).order_by('-rank')

        logging.debug("searching with keyword", keyword)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
