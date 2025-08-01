from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def ready_check(request):
    if request.method == 'GET':
        return Response({'status': 'Ready. Talk is cheap, show me the code 🚀'})


@api_view(['GET'])
def health_check(request):
    if request.method == 'GET':
        return Response({'status': 'Healthy. Talk is cheap, show me the code 🚀'})
