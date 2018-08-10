from django.contrib.auth import get_user_model
from rest_framework import serializers
from construbot.users.models import Customer, Company, User


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
