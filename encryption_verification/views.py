from django.shortcuts import render
import json
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from .models import EncryptionInfo ,Product
from .serializer import ProductSerializer
from rest_framework import viewsets , status
from rest_framework.permissions import IsAdminUser , AllowAny ,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import base64
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta


ENCRYPTION_TIMEOUT = 24 * 60 * 60

@swagger_auto_schema(
    method='post',  #! 指定HTTP请求方法
    request_body=openapi.Schema(  #! 定義請求架構
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={  #! 定義回傳的訊息
        200: "'encrypted_value': 'string', 'private_key': 'string'",
        400: 'Bad Request',
    },
)

@csrf_exempt  
@api_view(['POST','GET'])
def create_encryption(request):
    if request.method == 'POST':
        # Your view logic here
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        current_time = timezone.now()

        # Generate a random string and encrypt it using RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        random_string = b'abcdefghijklmnopqrstuvwxyz' 
        encrypted_value = private_key.public_key().encrypt(
            random_string,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        expiration_time = current_time + timedelta(hours=24)

        # Serialize private key to store it for decryption later
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Store encrypted_value and private_key_pem in your database
        encryption_info = EncryptionInfo(
            username=username,
            password=password,
            encrypted_value=encrypted_value,
            private_key_pem=private_key_pem.decode('utf-8'),
            # expiration_time=expiration_time #!如果要加上24小時限制，在model需要加上此欄位
        )
        encryption_info.save()

        # Start the 24-hour timer here
        
        return JsonResponse({'encrypted_value': encrypted_value.hex(), 'private_key': private_key_pem.decode('utf-8')})


@swagger_auto_schema(
    method='post',  #! 指定HTTP请求方法
    request_body=openapi.Schema(  #! 定義請求架構
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'decrypted_value': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={  #! 定義回傳的訊息
        200: "驗證成功",
        400: '驗證失敗',
    },
)

@csrf_exempt
@api_view(['POST','GET'])
def verify_decryption(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        decrypted_value_base64  = data.get('decrypted_value')

        # Retrieve private_key_pem from your database based on username and password
        try:
            encryption_info = EncryptionInfo.objects.get(username=username, password=password)
        except EncryptionInfo.DoesNotExist:
            return JsonResponse({'message': 'User not found'})

        private_key_pem = encryption_info.private_key_pem

        # Deserialize private key
        private_key = serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None, backend=default_backend())

        # Convert the decrypted_value_hex to bytes
        decrypted_value = base64.b64decode(decrypted_value_base64)

        # Decrypt the value using private key
        decrypted_data = private_key.decrypt(
            decrypted_value,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        if decrypted_data == b'abcdefghijklmnopqrstuvwxyz':
            return JsonResponse({'message': '驗證成功'})
        else:
            return JsonResponse({'message': '驗證失敗'})
        


@swagger_auto_schema(
    method='post',  #! 指定HTTP请求方法
    request_body=openapi.Schema(  #! 定義請求架構
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'sql': openapi.Schema(type=openapi.TYPE_STRING), 
        }
    ),
    responses={  #! 定義回傳的訊息
        200: "完成測試",
        400: '帳號密碼有誤',
    },
)


@api_view(['POST','GET'])
@csrf_exempt
def sql_test(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')

    queryset = EncryptionInfo.objects.filter(username = username, password = password)

    if not queryset.exists():
        result = {"message": "帳號密碼有誤"}
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

    sql_query = data.get('sql')

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        results = cursor.fetchall()

    return JsonResponse({"message":"完成測試","results": results})
