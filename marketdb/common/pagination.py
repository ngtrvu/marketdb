from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from common.utils.logger import logger


class CustomPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "paging": {
                    "count": self.page.paginator.count,
                    "page": self.page.number,
                    "page_count": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
                "items": data,
            }
        )


class CustomJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}

        resource = None
        try:
            resource = getattr(
                renderer_context.get("view").get_serializer().Meta,
                "singular_resource_name",
                "item",
            )
        except AttributeError as e:
            logger.error(f"Error getting resource name: {e}")

        if resource and data and not data.get("paging"):
            response_data[resource] = data
        else:
            response_data = data

        response = super().render(response_data, accepted_media_type, renderer_context)
        return response
