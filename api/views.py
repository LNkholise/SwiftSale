from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from django.http import JsonResponse
from utils.web3_utils import Web3Handler
import json

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def buy_request(request):
    """
    Handles the entire buy process:
    - Create unsigned transaction
    - Frontend signs it
    - Backend broadcasts it to the blockchain
    - Check product quantity and update the stock accordingly
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body)

            # Extract wallet address and other parameters
            sender_address = data['sender']  # Get wallet address from frontend
            amount_in_usdt = data['amount']
            product_name = data['product_name']	
            product_quantity = data['product_quantity']
            signed_transaction = data.get('signed_transaction')  # Optional
            
            # Retrieve the product from the database
            try:
                product = Product.objects.get(name=product_name)  # Get the product by its name
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Product not found'
                }, status=404)
                
            # Check if the requested quantity is available in stock
            if product.quantity <= product_quantity:
                return JsonResponse({
                    'success': False,
                    'error': 'Insufficient stock available for the requested quantity'
                }, status=400)
                
            # Initialize Web3Handler for USDT contract
            contract_abi_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
            usdt_handler = Web3Handler(contract_address= contract_abi_address)  # USDT contract address

            if not signed_transaction:
                # Create unsigned transaction if no signed transaction is provided
                unsigned_tx = usdt_handler.create_unsigned_transaction(
                    sender_address=sender_address,
                    amount=amount_in_usdt,
                )

                # Return unsigned transaction to frontend for signing
                return JsonResponse({
                    'success': True,
                    'unsigned_transaction': unsigned_tx
                })

            # If the signed_transaction exists, broadcast it to the blockchain
            tx_hash = usdt_handler.broadcast_transaction(signed_transaction)
            
            # Updating the product stock after thhe signed_transaction is broadcasted
            with transaction.atomic():
                product.quantity -= product_quantity
                product.save()

            # Return the transaction hash in the response
            return JsonResponse({
                'success': True,
                'transaction_hash': tx_hash
            })

        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

