from rest_framework import viewsets
from rest_framework.views import APIView
from .auth_serializers import RegisterSerializer
from .utils.security import encode_payload


class RegistrationViewset(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = RegisterSerializer


    def post(self, request, *args, **kwargs):
        serializer  = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(user.id)
        sub = {
            "email": user.email,
            "id": str(user.id)
        }
        payload = encode_payload(sub)
        print(payload)
