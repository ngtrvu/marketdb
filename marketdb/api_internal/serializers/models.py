from rest_framework import serializers


class BulkUpdateSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    values = serializers.JSONField(required=True)
    conditions = serializers.JSONField(required=False)
