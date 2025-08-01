from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils.data import intersection, sub_dict
from common.utils.logger import logger
from api_internal.serializers.models import (
    BulkUpdateSerializer,
)


class BulkUpdateView(APIView):
    def post(self, request, format=None):
        serializer = BulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            model_name = serializer.data["model_name"]
            values = serializer.data["values"]
            conditions = serializer.data.get("conditions")

            if not isinstance(values, dict) or (conditions and not isinstance(conditions, dict)):
                return Response(
                    {"error": "Invalid values or conditions"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                model = apps.get_model("core", model_name)
            except Exception as ex:
                logger.warning(ex)
                return Response(
                    {"error": f"Invalid model name: {model_name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            model_fields = [f.name for f in model._meta.get_fields()]
            update_fields: list = list(values.keys())

            # bulk update with given data & conditions
            try:
                kargs = sub_dict(update_fields, values)
                queryset = model.objects.all()

                if conditions:
                    queryset = queryset.filter(**conditions)

                results = queryset.update(**kargs)
                return Response(
                    {
                        "success": True,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as ex:
                logger.warning(ex)
                return Response(
                    {"error": f"Bulk update failed: {ex}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
