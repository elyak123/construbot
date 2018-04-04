from django.db import models
from users.models import User
from core.utils import Round, get_directory_path
from django.db.models import Sum, F


# Create your models here.
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

    class Meta:
        verbose_name = 'Estimacion'
        verbose_name_plural = 'Estimaciones'

    def __str__(self):
        return self.descripcion


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