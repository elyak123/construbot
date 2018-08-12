from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer, UserSerializer
from construbot.users.models import User, Company, Customer
from django.contrib.auth.models import Group
from django.conf import settings
import time
import random

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

@api_view(['POST'])
def create_customer_user_and_company(request):
    name = settings.UUID+'+'+str(time.time())
    pwd = str(time.time()+random.random()*2000)
    if request.method == 'POST':
        group_a = Group.objects.get(name='Administrators')
        group_p = Group.objects.get(name='Proyectos')
        group_u = Group.objects.get(name='Users')
        customer = Customer.objects.create(customer_name=request.data['customer'])
        company = Company.objects.create(customer=customer, company_name=name)
        user = User.objects.create_user(
            customer=customer,
            username=name,
            email=request.data['email'],
            password=pwd,
        )
        user.company = [company.id]
        user.groups.add(*[group_a, group_p, group_u])
        import pdb; pdb.set_trace()
        return Response({'email': user.email, 'res': pwd})
