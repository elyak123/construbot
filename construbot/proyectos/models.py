from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Sum, F
from construbot.core import utils
from construbot.users.models import Company


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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

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
    destinatario_text = models.CharField(max_length=80)
    puesto = models.CharField(max_length=50, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

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
    fecha = models.DateField()
    contrato_name = models.CharField(max_length=300)
    contrato_shortName = models.CharField(max_length=80)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    sitio = models.ForeignKey(Sitio, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    file = models.FileField(upload_to=utils.get_directory_path, blank=True, null=True)
    monto = models.DecimalField('monto', max_digits=12, decimal_places=2, default=0.0)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    anticipo = models.DecimalField('anticipo', max_digits=4, decimal_places=2, default=0.0)

    def get_absolute_url(self):
        return reverse('construbot.proyectos:contrato_detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return self.contrato_name


class Retenciones(models.Model):
    TYPES = (
        ('AMOUNT', 'Monto'),
        ('PERCENTAGE', 'Porcentaje'),
    )
    nombre = models.CharField(max_length=80)
    valor = models.DecimalField('valor', max_digits=12, decimal_places=2, default=0.0)
    tipo = models.CharField(
        max_length=21, choices=TYPES, default='PERCENTAGE'
    )
    project = models.ForeignKey(Contrato, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Retención'
        verbose_name_plural = 'Retenciones'

    def __str__(self):
        return self.nombre


class Units(models.Model):
    unit = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return self.unit


class Estimate(models.Model):
    project = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    consecutive = models.IntegerField()
    draft_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='draft_by', on_delete=models.CASCADE)
    supervised_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='supervised_by', on_delete=models.CASCADE)
    start_date = models.DateField('start_date')
    finish_date = models.DateField('finish_date')
    draft_date = models.DateField('draft_date', auto_now=True)
    auth_by = models.ManyToManyField(Destinatario, blank=True)
    auth_by_gen = models.ManyToManyField(Destinatario, blank=True, related_name='generator')
    auth_date = models.DateField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoiced = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('proyectos:contrato_detail', kwargs={'pk': self.project.id})

    def total_estimate(self):
        total = self.estimateconcept_set.all().aggregate(
            total=utils.Round(Sum(F('cuantity_estimated') * F('concept__unit_price'))))
        return total

    def anotaciones_conceptos(self):
        conceptos = Concept.especial.filter(estimate_concept=self).order_by('pk')
        return conceptos.add_estimateconcept_properties(self.consecutive)

    class Meta:
        verbose_name = 'Estimacion'
        verbose_name_plural = 'Estimaciones'


class ConceptSet(models.QuerySet):

    def estimado_a_la_fecha(self, estimate_consecutive):
            estimateconcept = EstimateConcept.especial.estimado_a_la_fecha(estimate_consecutive)
            return self.annotate(
                acumulado=models.Subquery(
                    estimateconcept,
                    output_field=models.DecimalField()
                )
            )

    def estimado_anterior(self, estimate_consecutive):
        estimateconcept = EstimateConcept.especial.estimado_anterior(estimate_consecutive)
        return self.annotate(
            anterior=models.Subquery(
                estimateconcept,
                output_field=models.DecimalField()
            )
        )

    def esta_estimacion(self, estimate_consecutive):
        estimateconcept = EstimateConcept.especial.esta_estimacion(estimate_consecutive)
        return self.annotate(
            estaestimacion=models.Subquery(
                estimateconcept,
                output_field=models.DecimalField()
            )
        )

    def add_estimateconcept_ids(self, estimate_consecutive):
        conceptos_estimacion = EstimateConcept.especial.filtro_esta_estimacion(estimate_consecutive).filter(
            concept=models.OuterRef('pk')
        ).values('id')
        return self.annotate(
            conceptoestimacion=models.Subquery(
                conceptos_estimacion, output_field=models.IntegerField()
            )
        )

    def concept_image_count(self):
        return self.annotate(image_count=models.Count('estimateconcept__imageestimateconcept'))

    def get_largo_alto_ancho(self, estimate_consecutive):
        conceptos_estimacion = EstimateConcept.especial.filtro_esta_estimacion(estimate_consecutive).filter(
            concept=models.OuterRef('pk')
        )
        largo = conceptos_estimacion.values('largo')
        ancho = conceptos_estimacion.values('ancho')
        alto = conceptos_estimacion.values('alto')
        return self.annotate(
            largo=models.Subquery(
                largo, output_field=models.DecimalField(decimal_places=2)
            ),
            ancho=models.Subquery(
                ancho, output_field=models.DecimalField(decimal_places=2)
            ),
            alto=models.Subquery(
                alto, output_field=models.DecimalField(decimal_places=2)
            ),
        )

    def get_observations(self, estimate_consecutive):
        conceptos_estimacion = EstimateConcept.especial.filtro_esta_estimacion(estimate_consecutive).filter(
            concept=models.OuterRef('pk')
        ).values('observations')
        return self.annotate(
            observations=models.Subquery(
                conceptos_estimacion, output_field=models.TextField()
            )
        )

    def total_imagenes_estimacion(self):
        return self.aggregate(total_images=models.Sum('image_count'))

    def importe_total_esta_estimacion(self):
        return self.aggregate(total=Sum('estaestimacion'))

    def importe_total_anterior(self):
        return self.aggregate(total=Sum('anterior'))

    def importe_total_acumulado(self):
        return self.aggregate(total=Sum('acumulado'))

    def importe_total_contratado(self):
        return self.aggregate(total=Sum(F('unit_price') * F('total_cuantity')))

    def add_estimateconcept_properties(self, estimate_consecutive):
        return (
                self
                .estimado_a_la_fecha(estimate_consecutive)
                .estimado_anterior(estimate_consecutive)
                .esta_estimacion(estimate_consecutive)
                .add_estimateconcept_ids(estimate_consecutive)
                .concept_image_count()
                .get_largo_alto_ancho(estimate_consecutive)
                .get_observations(estimate_consecutive)
        )


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

    objects = models.Manager()
    especial = ConceptSet.as_manager()

    class Meta:
        verbose_name = 'Concepto'
        verbose_name_plural = 'Conceptos'

    def __str__(self):
        return self.concept_text

    def importe_contratado(self):
        return self.unit_price * self.total_cuantity

    def unit_price_operations(self, attr):
        if hasattr(self, attr):
            new_attr = getattr(self, attr)
        else:
            raise AttributeError(
                'El atributo %s no existe en %s, es necesario ejecutar '
                'add_estimateconcept_properties desde la instancia'
                'de una Estimación.' % (attr, self.concept_text)
                )
        if new_attr is not None:
            return new_attr / self.unit_price
        else:
            from decimal import Decimal
            return Decimal('0.00')

    def cantidad_estimado_anterior(self):
        return self.unit_price_operations('anterior')

    def cantidad_estimado_ala_fecha(self):
        return self.unit_price_operations('acumulado')

    def cantidad_esta_estimacion(self):
        return self.unit_price_operations('estaestimacion')

    def anotar_imagenes(self):
        if hasattr(self, 'conceptoestimacion'):
            return ImageEstimateConcept.objects.filter(estimateconcept=self.conceptoestimacion)
        else:
            raise AttributeError('No es posible realizar la operación porque es necesario '
                                 'que se ejecute add_estimateconcept_properties o al menos '
                                 'add_estimateconcept_ids desde la instancia de un QuerySet '
                                 'con el manejador ConceptSet')


class ECSet(models.QuerySet):

    def apuntar_total_estimado(self):
        return self.annotate(
            estimado=Sum(F('cuantity_estimated') * F('concept__unit_price')),
        ).values('estimado').filter(concept=models.OuterRef('pk'))

    def filtro_estimado_a_la_fecha(self, estimate_consecutive):
        return self.filter(
                estimate__consecutive__lte=estimate_consecutive,
                # concept=models.OuterRef('pk')
            ).order_by().values('concept')

    def filtro_estimado_anterior(self, estimate_consecutive):
        consecutivo = estimate_consecutive - 1
        return self.filter(
                estimate__consecutive=consecutivo,
                # concept=models.OuterRef('pk')
            ).order_by().values('concept')

    def filtro_esta_estimacion(self, estimate_consecutive):
        return self.filter(
                estimate__consecutive=estimate_consecutive,
                # concept=models.OuterRef('pk')
            ).order_by().values('concept')

    def estimado_anterior(self, estimate_consecutive):
        return self.filtro_estimado_anterior(estimate_consecutive).apuntar_total_estimado()

    def estimado_a_la_fecha(self, estimate_consecutive):
        return self.filtro_estimado_a_la_fecha(estimate_consecutive).apuntar_total_estimado()

    def esta_estimacion(self, estimate_consecutive):
        return self.filtro_esta_estimacion(estimate_consecutive).apuntar_total_estimado()


class EstimateConcept(models.Model):
    """
        Intermediate model for ManytoManyField between Concept and Estimate
    """
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    cuantity_estimated = models.DecimalField('cuantity_estimated', max_digits=12, decimal_places=2)
    observations = models.TextField(blank=True, null=True)
    largo = models.DecimalField('largo', max_digits=10, decimal_places=2, default=0)
    ancho = models.DecimalField('ancho', max_digits=10, decimal_places=2, default=0)
    alto = models.DecimalField('alto', max_digits=10, decimal_places=2, default=0)
    objects = models.Manager()
    especial = ECSet.as_manager()

    class Meta:
        verbose_name = 'Estimado por Concepto'
        verbose_name_plural = 'Estimaciones por Conceptos'

    def __str__(self):
        return self.concept.concept_text + str(self.cuantity_estimated)


class ImageEstimateConcept(models.Model):
    image = models.ImageField(upload_to=utils.get_image_directory_path)
    estimateconcept = models.ForeignKey(EstimateConcept, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Imagen_generador'
        verbose_name_plural = 'Imagenes_generadores'

    def __str__(self):
        return '{} {}'.format(self.id, repr(self.estimateconcept))
