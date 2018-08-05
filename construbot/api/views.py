from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from construbot.users.models import Customer
from construbot.api.serializers import CustomerSerializer

# Create your views here.


@csrf_exempt
def customer_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        customers = Customer.objects.all()
        customer = CustomerSerializer(customers, many=True)
        return JsonResponse(customer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        customer = CustomerSerializer(data=data)
        if customer.is_valid():
            customer.save()
            return JsonResponse(customer.data, status=201)
        return JsonResponse(customer.errors, status=400)
