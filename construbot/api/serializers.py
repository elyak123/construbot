from rest_framework import serializers
from construbot.users.models import Customer, Company, User


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('__all__')
