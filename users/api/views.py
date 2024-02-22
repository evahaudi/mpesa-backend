from rest_framework import generics, status
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from django.views import View
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.models import Payment,PaymentTransaction
import base64
from django.conf import settings
import requests
import json
from .permissions import  IsManagerUser
from users.models import  Payment,Users
from .serializers import (
    UsersSerializer,
    PaymentSerializer,
    ManagerSignupView,
   
   
)


class ManagerSignupView(generics.GenericAPIView):
    serializer_class = ManagerSignupView

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UsersSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": Token.objects.get(user=user).key,
                "message": "Account created successfully",
            }
        )



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)

        try:
            if not request.data:
                username = request.query_params.get("username")
                password = request.query_params.get("password")
                data = {"username": username, "password": password}
            else:
                data = request.data

            serializer = self.serializer_class(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            print("Validated Data:", serializer.validated_data)
            token, created = Token.objects.get_or_create(user=user)
            user_image_base64 = None
            if user.user_image:
                with open(user.user_image.path, "rb") as image_file:
                    user_image_base64 = base64.b64encode(image_file.read()).decode(
                        "utf-8"
                    )
            user_profile_data = {
                "user_id": user.pk,
                "is_chef": user.is_chef,
                "is_manager": user.is_manager,
                "is_waiter": user.is_waiter,
                "role": user.role,
                "email": user.email,
                "username": user.username,
                "fullname": user.fullname,
                "birthdate": user.birthdate,
                "location": user.location,
                "phone": user.phone,
                "department": user.department,
                "experienceyears": user.experienceyears,
                "user_image": user_image_base64,
            }
            return Response(
                {
                    "token": token.key,
                    "user_profile_data": user_profile_data,
                    "message": "Login successfully",
                }
            )
        except AuthenticationFailed as e:

            print(f"AuthenticationFailed: {e}")
            return Response({"error": str(e)}, status=400)
        except Exception as e:

            print(f"Exception: {e}")

            return HttpResponseServerError("Internal Server Error")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == "POST":
        try:

            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#Payment role manager ,waiter
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated & IsManagerUser]

    def post(self, request, *args, **kwargs):
        is_manager = request.user.is_authenticated and request.user.is_manager
    
        
        print("Is Manager:", is_manager)
        
        # Extract query parameters from request URL
        order = request.query_params.get('order')
        amount =request.query_params.get('amount') 
        payment_method =request.query_params.get('payment_method') 
        balance = request.query_params.get('balance')
        created_by = request.user.username 
        
        

        # Validate if all required parameters are provided
        if not (order and amount and payment_method and balance ):
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a dictionary with the data
        data = {
            'order': order,
            'payment_method': payment_method,
            'balance': balance,
            'amount': amount,
            'created_by': created_by,
        }
        data['created_by'] = request.user.pk
        print("data", data)
        print("username", created_by)
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['created_by'] = request.user
            payment = serializer.save()
            return Response(
                {
                    "payment": payment.payment_method,
                    "ammout":payment.amount,
                    "order":payment.order,
                    "balance":payment.balance,
                    "payment_deatals": PaymentSerializer(payment, context=self.get_serializer_context()).data,
                    "message": "Payment successful!!!",
                    'created_by': request.user.pk,
                },
                status=status.HTTP_201_CREATED  # Set status to 201 Created
            )
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  # Return 400 if any error occurs
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PaymentGetAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated & IsManagerUser ]

    def get_queryset(self):
        return Payment.objects.all()
    
class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated & IsManagerUser]

    def update(self, request, *args, **kwargs):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({"error": "ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        field_names = request.query_params.getlist('field_name')
        field_values = request.query_params.getlist('field_value')

        if len(field_names) != len(field_values):
            return Response({"error": "Number of field names and field values do not match"}, status=status.HTTP_400_BAD_REQUEST)

        for field_name, field_value in zip(field_names, field_values):
            if field_name not in ['amount', 'balance', 'payment', 'order']:
                return Response({"error": f"Invalid field name provided: {field_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
            setattr(payment, field_name, field_value)

        payment.save()
        
        return Response({"message": "Payment updated successfully"}, status=status.HTTP_200_OK)

class PaymentDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsManagerUser ]

    def delete(self, request, *args, **kwargs):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({"error": "ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)

        payment.delete()
        return Response({"message": "Trannsactions deleted  successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# class MpesaPaymentAPIView(APIView):
#     def post(self, request):
#         amount = request.data.get('amount')
#         phone_number = request.data.get('phone_number')
        
#         # Make a request to M-Pesa Daraja API to initiate payment
#         payload = {
#             'amount': amount,
#             'phone_number': phone_number,
#             # Other parameters
#         }
#         headers = {
#             'Authorization': 'Bearer ' + settings.MPESA_ACCESS_TOKEN,
#             'Content-Type': 'application/json'
#         }
#         response = requests.post(settings.MPESA_INITIATE_PAYMENT_URL, json=payload, headers=headers)
        
#         if response.status_code == 200:
#             return Response({'message': 'Payment initiated successfully'}, status=200)
#         else:
#             return Response({'message': 'Failed to initiate payment'}, status=400)

class MpesaPaymentAPIView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        phone_number = request.data.get('phone_number')
        
        # Make a request to M-Pesa Daraja API to initiate payment
        payload = {
            "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
            "Password": settings.MPESA_PASSWORD,
            "Timestamp": "20240222164939",  # You might need to generate this timestamp dynamically
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://mydomain.com/path",
            "AccountReference": "CompanyXLTD",
            "TransactionDesc": "Payment of X"
        }
        headers = {
            'Authorization': 'Bearer ' + settings.MPESA_ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        payload_json = json.dumps(payload)
        response = requests.post(settings.MPESA_INITIATE_PAYMENT_URL, json=payload, headers=headers , data=payload_json)
        print(response.json())
        
        if response.status_code == 200:
            return Response({'message': 'Payment initiated successfully'}, status=200)
        else:
            return Response({'message': 'Failed to initiate payment'}, status=400)
        
# class CallbackAPIView(APIView):
#     def post(self, request):
#         # Process the callback request here
#         # You can access request data like request.data
#         # Handle the M-Pesa API response and update your database or perform other actions as needed
        
#         # Return a response to acknowledge receipt of the callback
#         return HttpResponse('Callback received successfully', status=200)

class MPesaResponseSerializer(serializers.Serializer):
    TransactionID = serializers.CharField()
    Amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    ResultCode = serializers.CharField()

class CallbackAPIView(APIView):
    def post(self, request):
        # Deserialize the M-Pesa API response data
        serializer = MPesaResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mpesa_response = serializer.validated_data
        
        # Extract relevant data from the M-Pesa response
        transaction_id = mpesa_response.get('TransactionID')
        amount = mpesa_response.get('Amount')
        status = mpesa_response.get('ResultCode')
        
        # Update your database with the M-Pesa transaction details
        # For demonstration, assuming you have a PaymentTransaction model
        payment_transaction = PaymentTransaction.objects.get_or_create(transaction_id=transaction_id)[0]
        payment_transaction.amount = amount
        payment_transaction.status = status
        payment_transaction.save()
        
        # Return a response to acknowledge receipt of the callback
        return HttpResponse('Callback received and processed successfully', status=200)
        
        
        
        
        
# import requests
# url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
# querystring = {"grant_type":"client_credentials"}
# payload = ""
# headers = {
#   "Authorization": "Basic SWZPREdqdkdYM0FjWkFTcTdSa1RWZ2FTSklNY001RGQ6WUp4ZVcxMTZaV0dGNFIzaA=="
# }
# response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
# print(response.text)
