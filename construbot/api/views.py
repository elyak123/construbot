import time
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from construbot.users.models import Company, Customer, User
from construbot.api.serializers import CustomerSerializer, UserSerializer
from construbot.proyectos.models import Cliente, Sitio, Destinatario, Contrato, Estimate, Concept, Units, EstimateConcept
from construbot.users.models import Company
import json

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
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=request.user.customer
        )
        request.user.company.add(company)
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data['cliente_name']
        )
        return Response({'creado': cliente_created})

    @api_view(['POST'])
    def sitio_migration(request):
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=request.user.customer
        )
        request.user.company.add(company)
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
        company, company_created = Company.objects.get_or_create(
            company_name=request.data['company'],
            customer=request.user.customer
        )
        request.user.company.add(company)
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
    def contrato_concept_and_estimate_migration(request):
        json_data = json.loads(request.data)
        company, company_created = Company.objects.get_or_create(
            company_name=json_data['company'],
            customer=request.user.customer
        )
        request.user.company.add(company)
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=json_data['cliente']
        )
        sitio, sitio_created = Sitio.objects.get_or_create(
            cliente=cliente,
            sitio_name=json_data['sitio_name'],
            sitio_location=json_data['sitio_location']
        )
        contrato, contrato_created = Contrato.objects.get_or_create(
            folio=json_data['folio'],
            code=json_data['code'],
            fecha=json_data['fecha'],
            contrato_name=json_data['contrato_name'],
            contrato_shortName=json_data['contrato_shortName'],
            cliente=cliente,
            sitio=sitio,
            status=json_data['status'],
            monto=json_data['monto'],
            anticipo=0,
        )
        contrato.users.add(User.objects.get(username=settings.USERNAME_FOR_MIGRATION).id)
        contrato.save()
        get_concepts(contrato, json_data['concepts'])
        get_estimates(contrato, json_data['estimates'])
        return Response({'creado': contrato_created})


def get_concepts(contrato, concept_data):
    for concept in concept_data:
        unit, unit_created = Units.objects.get_or_create(
           unit=concept['unit']
        )
        concepto, concepto_created = Concept.objects.get_or_create(
            code=concept['code'],
            concept_text=concept['concept_text'],
            project=contrato,
            unit=unit,
            total_cuantity=concept['total_cuantity'],
            unit_price=concept['unit_price']
        )

def get_estimate_concepts(estimate, estimate_concepts):
    for estimate_concept_data in estimate_concepts:
        concept, c_created = Concept.objects.get_or_create(
            concept_text=estimate_concept_data['concept'],
            project=estimate.project,
        )
        estimate_concept, ec_created = EstimateConcept.objects.get_or_create(
            estimate=estimate,
            concept=concept,
            cuantity_estimated=estimate_concept_data['cuantity_estimated'],
            observations=estimate_concept_data['observations']
        )

def get_estimates(contrato, estimate_data):
    for estimacion in estimate_data:
        estimate, estimate_created = Estimate.objects.get_or_create(
            project=contrato,
            consecutive=estimacion['consecutive'],
            draft_by=User.objects.get(username=settings.USERNAME_FOR_MIGRATION),
            supervised_by=User.objects.get(username=settings.USERNAME_FOR_MIGRATION),
            start_date=estimacion['start_date'],
            finish_date=estimacion['finish_date'],
            draft_date=estimacion['draft_date'],
            auth_date=estimacion['auth_date'],
            paid=estimacion['paid'],
            invoiced=estimacion['invoiced'],
            payment_date=estimacion['payment_date'],
        )
        get_estimate_concepts(estimate, estimacion['estimate_concepts'])
        get_auth_by(estimate, estimacion['auth_by'], estimacion['auth_by_gen'])


def get_auth_by(estimate, auth_by_data, auth_by_gen_data):
    for auth_by_d in auth_by_data:
        auth_by, auth_by_created = Destinatario.objects.get_or_create(
            destinatario_text=auth_by_d['destinatario_text'],
            puesto=auth_by_d['puesto'],
            cliente=estimate.project.cliente
        )
        estimate.auth_by.add(auth_by)
    for auth_by_gen_d in auth_by_gen_data:
        auth_by_gen, auth_by_gen_created = Destinatario.objects.get_or_create(
            destinatario_text=auth_by_gen_d['destinatario_text'],
            puesto=auth_by_gen_d['puesto'],
            cliente=estimate.project.cliente
        )
        estimate.auth_by_gen.add(auth_by_gen)
