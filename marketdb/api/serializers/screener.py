from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer


class ScreenerSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)

    def to_representation(self, instance):
        data = instance.__dict__
        if "photo" in data and data["photo"]:
            data["photo"] = ImageHandlerSerializer().to_representation(data["photo"])

        del data["_state"]
        return data
