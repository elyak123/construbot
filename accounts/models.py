from django.db import models
from django.db                  import models
from django.utils               import timezone
from django.core.validators     import MaxValueValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Customer(models.Model):
    customer_name =  models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name        = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
      return self.customer_name

class Company(models.Model):
    full_name    = models.CharField(max_length=250, blank=True, null=True)
    company_name = models.CharField(max_length=120)
    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        verbose_name        = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
      return self.company_name

class ExtendUser(AbstractUser):
    company          = models.ManyToManyField(Company)
    customer         = models.ForeignKey(Customer, on_delete=models.CASCADE)
    currently_at     = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True, related_name='currently_at')
    bio              = models.TextField(max_length=500, blank=True)
    job_title        = models.CharField(max_length=30, blank=True)
    user_creation    = models.DateTimeField(auto_now_add=True)
    last_updated     = models.DateTimeField(auto_now=True)
    last_supervised  = models.DateTimeField(default=timezone.now)

    def __str__(self):
      return self.get_short_name()    

    def is_administrator(self):
        try:
            group = self.groups.get(name='Administrators')
            return True
        except:
            return False


    