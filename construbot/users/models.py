from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Customer(models.Model):
    customer_name = models.CharField(max_length=120, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):  # pragma: no cover
        return self.customer_name


@python_2_unicode_compatible
class Company(models.Model):
    full_name = models.CharField(max_length=250, blank=True, null=True)
    company_name = models.CharField(max_length=120)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.company_name  # pragma: no cover


class ExtendUserManager(UserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        try:
            Customer.objects.get(id=1)
        except ObjectDoesNotExist:
            Customer.objects.create()

        extra_fields.setdefault('customer', Customer.objects.all().first())

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self._create_user(username, email, password, **extra_fields)


@python_2_unicode_compatible
class User(AbstractUser):

    company = models.ManyToManyField(Company)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    currently_at = models.ForeignKey(
        Company, on_delete=models.SET_NULL, blank=True, null=True, related_name='currently_at'
    )
    user_creation = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_supervised = models.DateTimeField(default=timezone.now)
    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    objects = ExtendUserManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def is_administrator(self):
        try:
            self.groups.get(name='Administrators')
            return True
        except ObjectDoesNotExist:
            return False
