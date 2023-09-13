from django.db import models
from django.contrib import admin


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.product_name
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]     

class EncryptionInfo(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    encrypted_value = models.TextField()
    private_key_pem = models.TextField()
    # expiration_time = models.DateTimeField() 
    
    def __str__(self):
        return self.username
    
@admin.register(EncryptionInfo)
class EncryptionInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EncryptionInfo._meta.fields]     