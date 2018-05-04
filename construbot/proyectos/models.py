from django.db import models
from construbot.users.models import User, Company
from core.utils import Round, get_directory_path
from django.core.urlresolvers import reverse
from django.db.models import Sum, F


# Create your models here.
class Cliente(models.Model):
    """El modelo que representa la relación entre una
    empresa (Company) perteneciente al comprador (Customer)
    y su cliente (modelo actual)"""
    cliente_name = models.CharField(max_length=80, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('proyectos:cliente_detail', kwargs={'pk': self.id})

    def get_contratos_ordenados(self):
        return self.contrato_set.all().order_by('-fecha')

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.cliente_name


class Sitio(models.Model):
    sitio_name = models.CharField(max_length=80)
    sitio_location = models.CharField(max_length=80, null=True, blank=True)
    # cambiar esto a cliente en lugar de company
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('proyectos:sitio_detail', kwargs={'pk': self.id})

    def get_contratos_ordenados(self):
        return self.contrato_set.all().order_by('-fecha')

    class Meta:
        verbose_name = "Sitio"
        verbose_name_plural = "Sitios"

    def __str__(self):
        return self.sitio_name


class Destinatario(models.Model):
    # Discutir eliminar company de aqui
    # para acceder a el podemos hacer
    # self.model.filter(cliente__company__company_name='bla')
    company = models.ForeignKey(Company)
    # Discutir quitarlo, se usaba poco en la app anterior.
    tratamiento = models.CharField(max_length=10, null=True, blank=True)
    destinatario_text = models.CharField(max_length=80)
    puesto = models.CharField(max_length=50, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('proyectos:destinatario_detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = "Destinatario"
        verbose_name_plural = "Destinatarios"

    def __str__(self):
        return self.destinatario_text


class Contrato(models.Model):
    folio = models.IntegerField()
    code = models.CharField(max_length=35, null=True, blank=True)
    # contract_code = models.CharField(max_length=80, null=True, blank=True)
    fecha = models.DateField()
    contrato_name = models.CharField(max_length=300)
    contrato_shortName = models.CharField(max_length=80)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    sitio = models.ForeignKey(Sitio, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    # casa_habitacion = models.BooleanField(default=False)
    file = models.FileField(upload_to=get_directory_path, blank=True, null=True)
    monto = models.DecimalField('monto', max_digits=12, decimal_places=2, default=0.0)
    # fecha_esperada_terminacion = models.DateField('Fecha esperada de terminacion',
    #                                               blank=True, null=True)

    def get_absolute_url(self):
        return reverse('construbot.proyectos:contrato_detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return self.contrato_name


class Units(models.Model):
    unit = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return self.unit


class Estimate(models.Model):
    """
        Model that represents the estimate
    """
    project = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    consecutive = models.IntegerField()
    draft_by = models.ForeignKey(User, related_name='draft_by', on_delete=models.CASCADE)
    supervised_by = models.ForeignKey(User, related_name='supervised_by', on_delete=models.CASCADE)
    start_date = models.DateField('start_date')
    finish_date = models.DateField('finish_date')
    draft_date = models.DateField('draft_date', auto_now=True)
    auth_by = models.ManyToManyField(Destinatario, blank=True)
    auth_by_gen = models.ManyToManyField(Destinatario, blank=True, related_name='generator')
    auth_date = models.DateField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoiced = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def total_estimate(self):
        total = self.estimateconcept_set.all().aggregate(
            total=Round(Sum(F('cuantity_estimated') * F('concept__unit_price'))))
        return total

    def get_concept_total(self):
        total_concept = self.concept_set.annotate(
            total_concept_amount=Round(
                F('total_cuantity') * F('unit_price')
            ),).order_by('id')

        lista = []
        dicc_totales = {}
        resultado = {}
        total_project_amount = total_concept.aggregate(total=Round(
            Sum(
                F('total_cuantity') * F('unit_price')
            )))["total"]
        current_total_amount = 0
        previous_total_amount = 0
        historical_amount = 0
        for concept in total_concept:
            dicc = {}
            current_total = concept.estimateconcept_set.filter(
                estimate=self,
            ).annotate(
                current_amount=Round(
                    F('cuantity_estimated') * F('concept__unit_price')
                )
            )
            current_total_amount += current_total.first().current_amount
            if self.consecutive > 1:
                prev_est = concept.estimateconcept_set.filter(
                    estimate__consecutive=self.consecutive - 1,
                ).annotate(
                    prev_amount=Round(
                        F('cuantity_estimated') * F('concept__unit_price')
                    )
                )
                dicc['prev_est'] = prev_est.first()
                previous_total_amount += prev_est.first().prev_amount

            all_prev_est = concept.estimateconcept_set.filter(
                estimate__consecutive__lte=self.consecutive,
            ).aggregate(
                all_prev_amount=Round(
                    Sum(F('cuantity_estimated') * F('concept__unit_price'))
                ),
                all_prev_estimated=Round(
                    Sum(F('cuantity_estimated'))
                )
            )
            historical_amount += all_prev_est["all_prev_amount"]
            dicc['concept'] = concept
            dicc['estimate_concept'] = current_total.first()
            dicc['all_previous_est'] = all_prev_est
            lista.append(dicc)
        dicc_totales['total_project_amount'] = total_project_amount
        dicc_totales['current_total_amount'] = current_total_amount
        dicc_totales['previous_total_amount'] = previous_total_amount
        dicc_totales['historical_amount'] = historical_amount
        resultado["conceptos"] = lista
        resultado["totales"] = dicc_totales
        return resultado

    class Meta:
        verbose_name = 'Estimacion'
        verbose_name_plural = 'Estimaciones'

    # def __str__(self):
    #     return self.nombre


class Concept(models.Model):
    """
        Model that represents an estimate concept
    """
    code = models.CharField(max_length=50)
    concept_text = models.TextField()
    project = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    estimate_concept = models.ManyToManyField(Estimate, through='EstimateConcept')
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    total_cuantity = models.DecimalField('cuantity', max_digits=12, decimal_places=2, default=0.0)
    unit_price = models.DecimalField('unit_price', max_digits=12, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = 'Concepto'
        verbose_name_plural = 'Conceptos'

    def __str__(self):
        return self.concept_text


class EstimateConcept(models.Model):
    """
        Intermediate model for ManytoManyField between Concept and Estimate
    """
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    cuantity_estimated = models.DecimalField('cuantity_estimated', max_digits=12, decimal_places=2)
    observations = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Estimado por Concepto'
        verbose_name_plural = 'Estimaciones por Conceptos'

    def __str__(self):
        return self.concept.concept_text + str(self.cuantity_estimated)
