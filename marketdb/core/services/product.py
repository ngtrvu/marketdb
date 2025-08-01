from django.db.models import OuterRef, Subquery

from core.services.base import BaseService
from core.models.screener.collection import Metric


class ProductService(BaseService):

    main_model = None
    meta_models = None
    join_field = ''
    mapping_fields = {}
    override_mapping_fields = {}

    fields = []
    filters = []
    sorts = []

    supported_operator = [
        'gt', 'gte', 'lt', 'lte', 'in', 'exact', 'iexact', 'contains', 'icontains', 'eq', 'ne', 'startswith',
        'istartswith', 'endswith', 'iendswith', 'isnull'
    ]

    """
    @param: fields: ['name', 'symbol', 'marketcap']
    @param: filters: [{'name': 'market_cap', 'operator': 'gte', 'value': 800000000000}]
    @param: sorts: [{'name': 'market_cap', 'type': 'desc'}]
    """
    def __init__(self, fields=[], filters=[], sorts=[]):
        self.mapping_fields = self.__generate_mapping_fields()
        self.filters = filters
        self.sorts = sorts

        filter_fields = [item.get('name') for item in filters]
        sort_fields = [item.get('name') for item in sorts]
        self.fields = fields + filter_fields + sort_fields

    def __generate_mapping_fields(self) -> dict:
        for model_cls in self.meta_models:
            for f in model_cls._meta.get_fields():
                f_name = f.name
                self.mapping_fields[f_name] = {
                    'model': model_cls,
                    'field': f_name
                }

        for field_name, model_cls in self.override_mapping_fields.items():
            self.override_mapping_fields[field_name] = {
                'model': model_cls,
                'field': field_name
            }

        return self.mapping_fields

    def __is_valid_field(self, field) -> bool:
        is_in_meta_model = self.mapping_fields.get(field, {}).get('field')
        is_in_main_model = getattr(self.main_model, field, False)
        return is_in_meta_model or is_in_main_model

    def __get_queryset(self):
        queryset = self.main_model.objects
        for item in self.fields:
            model_cls, field_name = self.mapping_fields.get(item, {}).get('model'), self.mapping_fields.get(item, {}).get('field')
            if not model_cls or not field_name:
                continue

            if getattr(self.main_model, field_name, False):
                continue

            join_expression = {self.join_field: OuterRef(self.join_field)}
            annotate_expression = {field_name: Subquery(model_cls.objects.filter(**join_expression).values(field_name)[:1])}
            queryset = queryset.annotate(**annotate_expression)

        for item in self.filters:
            field, operator, value = item.get('name'), item.get('operator'), item.get('value')
            if not self.__is_valid_field(field):
                continue

            # TODO: fix duplicated field names
            filter_expression = {"{0}".format(field): value}
            if operator and operator in self.supported_operator:
                if operator == 'in':
                    filter_expression = {"{0}__{1}".format(field, operator): value.split(';')}
                elif operator != 'eq':
                    filter_expression = {"{0}__{1}".format(field, operator): value}

            queryset = queryset.filter(**filter_expression)

        for item in self.sorts:
            field, sort_type = item.get('name'), item.get('type')
            if not self.__is_valid_field(field):
                continue

            if sort_type == 'asc':
                sort_str = "{0}".format(field)
            elif sort_type == 'desc':
                sort_str = "-{0}".format(field)
            else:
                continue

            queryset = queryset.order_by(sort_str)

        return queryset

    def get_supported_operators(self):
        return [
            {'value': 'gt', 'label': '>'},
            {'value': 'gte', 'label': '>='},
            {'value': 'lt', 'label': '<'},
            {'value': 'lte', 'label': '<='},
            {'value': 'in', 'label': 'IN'},
            {'value': 'eq', 'label': 'Equal'},
        ]

    def get_supported_fields(self, product_type):
        result = []

        metrics = Metric.objects.filter(product_type=product_type).all()
        for metric in metrics:
            result.append({
                'value': metric.name,
                'label': metric.label,
                'group': metric.group,
            })

        return result

    def is_valid(self) -> bool:
        return True

    def call(self):
        if not self.is_valid():
            return []

        queryset = self.__get_queryset()
        return queryset.all()
