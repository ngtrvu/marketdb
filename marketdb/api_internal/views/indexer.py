from itertools import groupby
from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils.data import intersection, sub_dict
from common.utils.logger import logger
from api_internal.serializers.indexer import (
    BulkIndexerSerializer,
    IndexerSerializer,
)


def get_model_name(model_name: str) -> str:
    app_name = "core"
    if model_name.find(".") > 0:
        app_name = model_name.split(".")[0]
        if not app_name or app_name not in apps.app_configs:
            raise Exception(f"Invalid app name: {app_name}")
        model_name = model_name.split(".")[1]

    return app_name, model_name


def dedup_instances(items, key_fields):
    """Deduplicate items based on key fields, keeping the last occurrence"""

    # Create a tuple of key values for each item
    def get_key(item):
        return tuple(getattr(item, field) for field in key_fields)

    # Sort by keys to group duplicates together
    sorted_items = sorted(items, key=get_key)

    # Keep only the last item for each key combination
    unique_items = {}
    for key, group in groupby(sorted_items, key=get_key):
        # Convert to list and take the last item
        unique_items[key] = list(group)[-1]

    return list(unique_items.values())


class IndexerView(APIView):
    def post(self, request, format=None):
        serializer = IndexerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                key_name = serializer.data["key_name"]
                key_value = serializer.data["key_value"]
                kargs = {}
                kargs[key_name] = key_value

                model_name = serializer.data["model_name"]
                app_name, model_name = get_model_name(model_name)
                model = apps.get_model(app_name, model_name)
                payload = serializer.data["payload"]
                model.objects.update_or_create(**kargs, defaults=payload)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as ex:
                logger.warning(ex)
                return Response(
                    {"error": "Invalid input", "message": str(ex)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkIndexerView(APIView):
    def post(self, request, format=None):
        serializer = BulkIndexerSerializer(data=request.data)
        if serializer.is_valid():
            key_fields = serializer.data["key_fields"]
            model_name = serializer.data["model_name"]
            items = serializer.data["items"]

            try:
                app_name, model_name = get_model_name(model_name)
                model = apps.get_model(app_name, model_name)
            except Exception as ex:
                logger.warning(ex)
                return Response(
                    {"error": f"Invalid model name: {model_name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            model_fields = []
            for f in model._meta.get_fields():
                if f.is_relation:
                    # add column name with _id, e.g. industry_id
                    model_fields.append(f.name + "_id")
                elif not f.primary_key:
                    # only support non-primary key fields
                    model_fields.append(f.name)

            update_fields: list = []
            obj_items: list = []
            payload_fields: list = []
            warning_messages: list = []

            for item_data in items:
                try:
                    if not payload_fields:
                        payload_fields = item_data.keys()
                        update_fields = intersection(payload_fields, model_fields)
                    elif payload_fields != item_data.keys():
                        error_message = f"Payload fields are not the same: {payload_fields} {item_data.keys()}"
                        logger.warning(error_message)
                        return Response(
                            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
                        )

                    kargs = sub_dict(update_fields, item_data)
                    item = model(**kargs)

                    obj_items.append(item)
                except Exception as ex:
                    logger.warning(ex)
                    warning_messages.append(f"Invalid data: {ex}")

            # bulk create or update with given keys
            try:
                item_total = len(obj_items)
                if not item_total:
                    return Response(
                        {"error": ", ".join(warning_messages)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Deduplicate items before creating objects
                objs = model.objects.bulk_create(
                    dedup_instances(obj_items, key_fields),
                    update_conflicts=True,
                    unique_fields=key_fields,
                    update_fields=update_fields,
                )
                return Response(
                    {
                        "success": True,
                        "total": len(objs),
                        "warning": ", ".join(warning_messages),
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as ex:
                logger.warning(f"Failed on {model_name}: {ex}")
                return Response(
                    {"error": f"Failed on {model_name}: {ex}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
