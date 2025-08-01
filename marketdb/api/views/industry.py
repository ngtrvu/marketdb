from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.industries.industry import Industry
from api.serializers.industry import IndustrySerializer, IndustryDetailSerializer


class IndustryViewSet(ReadOnlyModelViewSet):
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    ordering = ('-created',)

    def get_queryset(self):
        self.queryset = self.queryset.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IndustryDetailSerializer
        return self.serializer_class
