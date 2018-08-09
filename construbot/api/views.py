from django.conf import settings
from rest_framework import generics
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer


class CustomerList(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class UserRetrive(generics.RetrieveAPIView):
    lookup_field = 'email'

    def get_queryset(self):
        user_model = settings.AUTH_USER_MODEL
        return user_model.objects
