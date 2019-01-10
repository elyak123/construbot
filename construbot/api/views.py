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
from construbot.proyectos.models import Cliente, Sitio, Destinatario, Contrato, Estimate
from construbot.users.models import Company

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


class DataMigration(object):
    @api_view(['POST'])
    def cliente_migration(request):
        customer, customer_created = Customer.objects.get_or_create(
            customer_name=request.data['customer']
        )
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=customer
        )
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data['cliente_name']
        )
        return Response({'creado': cliente_created})

    @api_view(['POST'])
    def sitio_migration(request):
        customer, customer_created = Customer.objects.get_or_create(
            customer_name=request.data['customer']
        )
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=customer
        )
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name='Migracion'
        )
        sitio, sitio_created = Sitio.objects.get_or_create(
            cliente=cliente,
            sitio_name=request.data['sitio_name'],
            sitio_location=request.data['sitio_location']
        )
        return Response({'creado': sitio_created})

    @api_view(['POST'])
    def destinatario_migration(request):
        customer, customer_created = Customer.objects.get_or_create(
            customer_name=request.data['customer']
        )
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=customer
        )
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data['cliente']
        )
        destinatario, destinatario_created = Destinatario.objects.get_or_create(
            cliente=cliente,
            destinatario_text=request.data['destinatario_text'],
            puesto=request.data['puesto']
        )
        return Response({'creado': destinatario_created})

    @api_view(['POST'])
    def contrato_and_concept_migration(request):
        customer, customer_created = Customer.objects.get_or_create(
            customer_name=request.data['customer']
        )
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=customer
        )
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data['cliente']
        )
        sitio, sitio_created = Sitio.objects.get_or_create(
            cliente=cliente,
            sitio_name=request.data['sitio_name'],
            sitio_location=request.data['sitio_location']
        )
        contrato, contrato_created = Contrato.objects.get_or_create(
            folio=request.data['folio'],
            code=request.data['code'],
            fecha=request.data['fecha'],
            contrato_name=request.data['contrato_name'],
            contrato_shortName=request.data['contrato_shortName'],
            cliente=cliente,
            sitio=sitio,
            status=request.data['status'],
            monto=request.data['monto'],
            anticipo=0,
        )
        return Response({'creado': contrato_created})

    @api_view(['POST'])
    def estimate_migration(request):
        customer, customer_created = Customer.objects.get_or_create(
            customer_name=request.data['customer']
        )
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=customer
        )
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data['cliente']
        )
        contrato, contrato_created = Contrato.objects.get_or_create(
            contrato_name=request.data['project'],
            cliente=cliente,
        )
        estimate, estimate_created = Estimate.objects.get_or_create(
            project=contrato,
            consecutive=request.data['consecutive'],
            start_date=request.data['start_date'],
            finish_date=request.data['finish_date'],
            draft_date=request.data['draft_date'],
            auth_date=request.data['auth_date'],
            paid=request.data['paid'],
            invoiced=request.data['invoiced'],
            payment_date=request.data['payment_date'],
        )
        return Response({'creado': estimate_created})
