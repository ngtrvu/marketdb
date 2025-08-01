from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.mixin import ContentStatusEnum
from core.models.funds.fund_nav import MutualFundNavIndex
from api.serializers.fund_nav import MutualFundNavSerializer


class MutualFundNavViewset(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    queryset = MutualFundNavIndex.objects.filter(fund__status=ContentStatusEnum.PUBLISHED).all()
    serializer_class = MutualFundNavSerializer
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    ordering = ("-nav",) # Default ordering
    ordering_fields = '__all__'
    filterset_fields = ['fund__type', 'fund__is_on_stag', 'fund__status']
    search_fields = ['fund__name', 'fund__symbol']
