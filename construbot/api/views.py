from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer, UserSerializer


class CustomerList(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class UserRetrive(generics.RetrieveAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects
    lookup_field = 'email'


@api_view(['POST'])
def email_uniqueness(request):
    if request.method == 'POST':
        User = get_user_model()
        try:
            user = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            user = None
        return Response({'unique': user is None})
