import time
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from construbot.users.models import Company, Customer
from construbot.api.serializers import CustomerSerializer, UserSerializer

User = get_user_model()


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
    if request.method == 'POST':
        group_a, a_created = Group.objects.get_or_create(name='Administrators')
        group_p, b_created = Group.objects.get_or_create(name='Proyectos')
        group_u, c_created = Group.objects.get_or_create(name='Users')
        customer = Customer.objects.create(customer_name=request.data['customer'])
        company = Company.objects.create(customer=customer, company_name=name)
        user = User(
            customer=customer,
            username=name,
            email=request.data['email'],
        )
        user.set_unusable_password()
        try:
            user.full_clean()
        except ValidationError as e:
            return Response({'success': False, 'errors': e})
        user.save()
        user.company = [company.id]
        user.groups.add(*[group_a, group_p, group_u])
        return Response(
            {
                'success': True,
                'id': user.id,
                'email': user.email,
                'usable': user.has_usable_password()
            }
        )


@api_view(['POST'])
def change_user_password(request):
    user = User.objects.get(id=request.data['id_usr'])
    user.set_password(request.data['pwd'])
    user.save()
    return Response({'pass': user.has_usable_password()})
