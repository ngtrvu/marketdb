from rest_framework import serializers


class TableExporterSerializer(serializers.Serializer):
    table_name = serializers.CharField(required=True)
    dataset_name = serializers.CharField(required=True)
    bucket_name = serializers.CharField(required=True)

    input_date = serializers.CharField(required=False, allow_blank=True)
    directory_name = serializers.CharField(required=False, allow_blank=True)
