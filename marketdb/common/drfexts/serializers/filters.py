from rest_framework import serializers


class FilterSerializer(serializers.Serializer):
    fields = serializers.CharField(max_length=500, required=False)
    filters = serializers.CharField(max_length=500, required=False)
    sorts = serializers.CharField(max_length=500, required=False)

    def validate_fields(self, value):
        if not value:
            return []

        return value.split(',')

    def validate_filters(self, value):
        if not value:
            return []

        result = []
        list_raw = value.split(',')
        for item in list_raw:
            values = item.split('__')
            if len(values) >= 3 and values[0] and values[1] and values[2]:
                result.append({'name': values[0], 'operator': values[1], 'value': values[2]})

        return result

    def validate_sorts(self, value):
        if not value:
            return []

        result = []
        list_raw = value.split(',')
        for item in list_raw:
            values = item.split('__')
            if len(values) >= 2 and values[0] and values[1]:
                result.append({'name': values[0], 'type': values[1]})

        return result
