from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Test API",
        default_version='v1',
        description="Your API description",
        terms_of_service="http://127.0.0.1:8000/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('create_encryption/', views.create_encryption, name='create_encryption'),
    path('verify_decryption/', views.verify_decryption, name='verify_decryption'),
    path('sql_test/', views.sql_test, name='sql_test'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
