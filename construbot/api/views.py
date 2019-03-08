import time
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework import generics
# Checar uso correcto
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
##
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from construbot.users.models import Company, Customer, NivelAcceso
from construbot.api.serializers import CustomerSerializer, UserSerializer
from construbot.proyectos.models import Cliente, Sitio, Destinatario, \
    Contrato, Estimate, Concept, Units, EstimateConcept

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
            user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            user = None
        return Response({'unique': user is None})


@api_view(['POST'])
def create_customer_user_and_company(request):
    group_a, a_created = Group.objects.get_or_create(name='Administrators')
    group_p, b_created = Group.objects.get_or_create(name='Proyectos')
    group_u, c_created = Group.objects.get_or_create(name='Users')
    customer = Customer.objects.create(customer_name=request.data.get('customer'))
    company = Company.objects.create(customer=customer, company_name=request.data.get('company'))
    nivel, nivel_created = NivelAcceso.objects.get_or_create(nivel=request.data.get('permission_level', 1))
    user = User(
        customer=customer,
        username=request.data.get('name'),
        email=request.data.get('email'),
        nivel_acceso=nivel
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
    user = User.objects.get(id=request.data.get('id_usr'))
    user.set_password(request.data.get('pwd'))
    user.save()
    return Response({'pass': user.has_usable_password()})


class WebHook(APIView):
    authentication_class = (BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        import pdb; pdb.set_trace()
        content = {
            'user': request.user,  # `django.contrib.auth.User` instance.
            'auth': request.auth,  # None
        }
        return Response(content)


class DataMigration(object):
    @api_view(['POST'])
    def cliente_migration(request):
        json_data = dict(request.data)
        for nombre, obj in json_data.items():
            company, company_created = Company.objects.get_or_create(
                company_name=obj['company'],
                customer=request.user.customer
            )
            request.user.company.add(company)
            cliente, cliente_created = Cliente.objects.get_or_create(
                company=company,
                cliente_name=obj['cliente_name']
            )
        return Response({'exito': True})

    @api_view(['POST'])
    def sitio_migration(request):
        json_data = dict(request.data)
        for nombre, obj in json_data.items():
            company, company_created = Company.objects.get_or_create(
                company_name=obj['company'],
                customer=request.user.customer
            )
            request.user.company.add(company)
            cliente, cliente_created = Cliente.objects.get_or_create(
                company=company,
                cliente_name='Migracion'
            )
            sitio, sitio_created = Sitio.objects.get_or_create(
                cliente=cliente,
                sitio_name=obj['sitio_name'],
                sitio_location=obj['sitio_location']
            )
        return Response({'exito': True})

    @api_view(['POST'])
    def destinatario_migration(request):
        company, company_created = Company.objects.get_or_create(
            company_name=request.data.get('company'),
            customer=request.user.customer
        )
        request.user.company.add(company)
        cliente, cliente_created = Cliente.objects.get_or_create(
            company=company,
            cliente_name=request.data.get('cliente')
        )
        destinatario, destinatario_created = Destinatario.objects.get_or_create(
            cliente=cliente,
            destinatario_text=request.data.get('destinatario_text'),
            puesto=request.data.get('puesto')
        )
        return Response({'creado': destinatario_created})

    @api_view(['POST'])
    def contrato_concept_and_estimate_migration(request):
        json_data = json.loads(request.data)
        for nombre, obj in json_data.items():
            company, company_created = Company.objects.get_or_create(
                company_name=obj['company'],
                customer=request.user.customer
            )
            request.user.company.add(company)
            cliente, cliente_created = Cliente.objects.get_or_create(
                company=company,
                cliente_name=obj['cliente']
            )
            try:
                sitio = Sitio.objects.get(sitio_name=obj['sitio_name'])
            except Sitio.DoesNotExist:
                sitio = Sitio.objects.create(
                    cliente=cliente,
                    sitio_name=obj['sitio_name'],
                    sitio_location=obj['sitio_location']
                )
            contrato, contrato_created = Contrato.objects.get_or_create(
                folio=obj['folio'],
                code=obj['code'],
                fecha=obj['fecha'],
                contrato_name=obj['contrato_name'],
                contrato_shortName=obj['contrato_shortName'],
                cliente=cliente,
                sitio=sitio,
                status=obj['status'],
                monto=obj['monto'],
                anticipo=0,
            )
            contrato.users.add(User.objects.get(username=request.user.username))
            contrato.save()
            get_concepts(contrato, obj['concepts'])
            get_estimates(contrato, obj['estimates'], request.user.username)
        return Response({'exito': True})


def get_concepts(contrato, concept_data):
    for concept in concept_data:
        unit, unit_created = Units.objects.get_or_create(
           unit=concept['unit'],
           company=contrato.cliente.company
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


def get_estimates(contrato, estimate_data, username):
    for estimacion in estimate_data:
        estimate, estimate_created = Estimate.objects.get_or_create(
            project=contrato,
            consecutive=estimacion['consecutive'],
            draft_by=User.objects.get(username=username),
            supervised_by=User.objects.get(username=username),
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
