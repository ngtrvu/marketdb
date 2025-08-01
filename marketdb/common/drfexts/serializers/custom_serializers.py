from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict


class LabelingKeyValueSerializer(serializers.ModelSerializer):

    def __init__(self, alias=None, label_mapping=None, items_field='items', **kwargs):
        super(LabelingKeyValueSerializer, self).__init__(**kwargs)
        if label_mapping is None:
            label_mapping = {"symbol": "Mã Cổ Phiếu"}
        self.label_mapping = label_mapping
        self.items_field = items_field

    # @property
    # def data(self):
    #     ret = super(LabelingKeyValueSerializer, self).data
    #     return ReturnDict(ret, serializer=self)
        # return ReturnDict(self.__change_format_data(ret), serializer=self)

    def __format_representation(self, representation: dict):
        print("**" * 80)
        print(representation)
        print("**" * 80)
        label_value_items = []
        for key, _ in representation.items():
            val = representation[key]

            if key not in self.label_mapping:
                # simple label key by remove underscore then upper the string
                label = key.replace("_", " ").upper()
            else:
                label = self.label_mapping[key]
            item = {
                "label": label,
                "key": key,
                "value": val
                # "ordering": 1
            }
            label_value_items.append(item)
        representation = {f"{self.items_field}": label_value_items}
        return representation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = self.__format_representation(representation)
        return representation
