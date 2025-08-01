from rest_framework import mixins, status
from rest_framework import serializers
from rest_framework.response import Response


class CreateModelMixin(mixins.CreateModelMixin):
    """
    Create a model instance with return detail instance
    """

    detail_serializer_class: serializers.ModelSerializer = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        if not self.detail_serializer_class:
            raise Exception("Make sure that the detail_serializer_class is set in your class")
        headers = self.get_success_headers(serializer.data)
        return Response(self.detail_serializer_class(instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()
