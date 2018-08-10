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

    def __str__(self):
        if self.customer_name is not None:
            return self.customer_name
        else:
            return str(self.id)


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
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        try:
            customer = Customer.objects.get(id=1)
        except ObjectDoesNotExist:
            customer = Customer.objects.create()
        extra_fields.setdefault('customer', customer)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self._create_user(email, password, **extra_fields)


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
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    objects = ExtendUserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def is_administrator(self):
        try:
            self.groups.get(name='Administrators')
            return True
        except ObjectDoesNotExist:
            return False
