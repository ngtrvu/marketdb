from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer as RestJSONRenderer
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'paging': {
                'count': self.page.paginator.count,
                'page': self.page.number,
                'page_count': self.page.paginator.num_pages,
                'page_size': 20,
            },
            'items': data
        })


class AdminPagination(DefaultPagination):
    page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'paging': {
                'count': self.page.paginator.count,
                'page': self.page.number,
                'page_count': self.page.paginator.num_pages,
                'page_size': 50,
            },
            'items': data
        })


class DefaultJSONRenderer(RestJSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}

        resource = None
        try:
            resource = getattr(renderer_context.get('view').serializer_class.Meta, 'singular_resource_name', 'item')
        except:
            pass

        if resource and isinstance(resource, str) and data and isinstance(data, dict) and not data.get('paging'):
            response_data[resource] = data
        else:
            response_data = data

        response = super(DefaultJSONRenderer, self).render(response_data, accepted_media_type, renderer_context)
        return response


# Deprecated
# TODO: Move marketdb use DefaultJSONRenderer instead to stand api format return
class JSONRenderer(RestJSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}

        resource = None
        try:
            resource = getattr(renderer_context.get('view').serializer_class.Meta, 'singular_resource_name')
        except:
            pass

        if resource and isinstance(resource, str) and data and isinstance(data, dict) and not data.get('paging'):
            response_data[resource] = data
        else:
            response_data = data

        response = super(JSONRenderer, self).render(response_data, accepted_media_type, renderer_context)
        return response
