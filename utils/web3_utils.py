from web3 import Web3
import json
import os
from django.conf import settings

class Web3Handler:
    def __init__(self, contract_address):
        self.w3 = Web3(Web3.HTTPProvider(settings.PROVIDER_URL))
        self.contract_address = self.w3.to_checksum_address(contract_address)

        # Load the contract ABI
        with open('utils/USDT.json', 'r') as abi_file:
            self.contract_abi = json.load(abi_file)

        # Initialize the contract
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def create_unsigned_transaction(self, sender_address, amount, gas=100000, gas_price_in_gwei=None, chain_id=1):
        sender_address = self.w3.to_checksum_address(sender_address)
        recipient_address = self.w3.to_checksum_address(settings.RECIPIENT_ADDRESS)
        
        amount_in_wei = self.w3.to_wei(amount, 'mwei')  # Convert USDT amount to smallest unit (6 decimals)
        nonce = self.w3.eth.get_transaction_count(sender_address)
        
        # Fetching gas price dynamically
        if not gas_price_in_gwei:
            gas_price_in_gwei = self.w3.eth.gas_price / (10 ** 9) # Gas converted from wei to gwei

        # Create unsigned transaction
        unsigned_tx = {
            'to': self.contract_address,
            'from': sender_address,
            'data': self.contract.encodeABI(fn_name='transfer', args=[recipient_address, amount_in_wei]),
            'gas': gas,
            'gasPrice': self.w3.to_wei(gas_price_in_gwei, 'gwei'),
            'nonce': nonce,
            'chainId': chain_id,
        }
        return unsigned_tx

    def get_wallet_balance(self, wallet_address):
        wallet_address = self.w3.to_checksum_address(wallet_address)
        return self.contract.functions.balanceOf(wallet_address).call()

    def broadcast_transaction(self, signed_transaction):
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction)
        return tx_hash.hex()

