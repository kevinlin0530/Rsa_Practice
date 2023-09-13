from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        # fields = '__all__'
        fields = [field.name for field in Product._meta.fields] 
