from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer


class CustomerList(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class UserRetrive(generics.RetrieveAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = CustomerSerializer
    lookup_field = 'email'

    def get_object(self):
        User = get_user_model()
        try:
        	user = User.objects.get(email=self.kwargs['email'])
        except User.DoesNotExist:
        	user = User.objects.none()
        return user
