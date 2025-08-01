from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils.logger import logger
from core.services.search.search_index import SearchReindexService


class SearchReindexingView(APIView):
    def post(self, request, format=None):
        try:
            service = SearchReindexService()
            success = service.call()
            if success:
                return Response(
                    {"success": True},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": service.get_error_message()},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            logger.warning(ex)
            return Response(
                {"error": f"Search reindex failed: {ex}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
