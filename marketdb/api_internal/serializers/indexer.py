from rest_framework import serializers


class IndexerSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    key_name = serializers.CharField(required=True)
    key_value = serializers.CharField(required=True)
    payload = serializers.JSONField(required=True)


class BulkIndexerSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    key_fields = serializers.ListField(required=True, child=serializers.CharField(max_length=255))
    items = serializers.JSONField(required=True)
