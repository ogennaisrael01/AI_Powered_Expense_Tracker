
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([]) 
def health(request):
    return Response({
        'success': True, 
        'message': 'Welcome to my AI powered budget tracker'
        }, 
        status=200)


