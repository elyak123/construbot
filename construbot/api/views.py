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
    lookup_field = 'email'

    def get_queryset(self):
        User = get_user_model()
        return User.objects
