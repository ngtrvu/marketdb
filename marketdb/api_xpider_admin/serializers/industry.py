from rest_framework import serializers

from xpider.models.industry import Industry


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = '__all__'
        singular_resource_name = 'item'
