from rest_framework import  status
from rest_framework.response import Response
from rest_framework.authtoken.views import  APIView
from datetime import datetime
from users.models import PaymentTransaction
     
class CallbackAPIView(APIView):
    def post(self, request):
        try:
            # Extract data from the request
            data = request.data.get('Body', {}).get('stkCallback', {})
            merchant_request_id = data.get('MerchantRequestID')
            checkout_request_id = data.get('CheckoutRequestID')
            result_code = data.get('ResultCode')
            result_desc = data.get('ResultDesc')
            callback_metadata = data.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract specific information from callback metadata
            amount = next((str(item['Value']) for item in callback_metadata if item['Name'] == 'Amount'), None)
            mpesa_receipt_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'), None)
            transaction_date = next((str(item['Value']) for item in callback_metadata if item['Name'] == 'TransactionDate'), None)
            phone_number = next((str(item['Value']) for item in callback_metadata if item['Name'] == 'PhoneNumber'), None)
            
            # Convert transaction date to a datetime object
            transaction_date = datetime.strptime(transaction_date, '%Y%m%d%H%M%S') if transaction_date else None
            
            
            # Save the transaction details to the database
            payment_transaction = PaymentTransaction.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                result_code=result_code,
                result_desc=result_desc,
                amount=amount,
                mpesa_receipt_number=mpesa_receipt_number,
                transaction_date=transaction_date,
                phone_number=phone_number
            )
            
             # Return a success response with additional transaction details
            response_data = {
                "message": "Callback received and processed successfully",
                "phone_number": payment_transaction.phone_number,
                "amount": payment_transaction.amount,
                "checkout_request_id": payment_transaction.checkout_request_id,
                "mpesa_receipt_number": payment_transaction.mpesa_receipt_number
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            # Return an error response if any exception occurs during processing
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
