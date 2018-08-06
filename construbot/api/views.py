from rest_framework import generics
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer


class CustomerList(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
