import json
import os
from web3 import Web3
from dotenv import load_dotenv
from services.email_notifications import send_email

load_dotenv()

with open('abi/cultstaking.json', 'r') as abi_file:
    abi = json.load(abi_file)

avalanche_rpc_url = os.getenv('RPC_PROD')
contract_address = "0xE08895b7ccAD796936CB3126d88d12692611ab59"
web3 = Web3(Web3.HTTPProvider(avalanche_rpc_url))

if not web3.isConnected():
    raise Exception("Failed to connect to Avalanche network")

contract = web3.eth.contract(address=contract_address, abi=abi)

def call_pray():
    PUB_KEY = os.getenv('PUB_KEY')
    PVT_KEY = os.getenv('PVT_KEY')

    try:
        gas_price = web3.eth.gasPrice
        gas_estimate = contract.functions.pray().estimateGas({'from': PUB_KEY})

        transaction = contract.functions.pray().buildTransaction({
            'from': PUB_KEY,
            'nonce': web3.eth.getTransactionCount(PUB_KEY),
            'gas': gas_estimate,
            'gasPrice': gas_price
        })

        signed_txn = web3.eth.account.signTransaction(transaction, private_key=PVT_KEY)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Transaction successful with hash: {tx_hash.hex()}")

        send_email(
            subject="Pray Transaction Successful",
            body=f"Transaction successful with hash: {tx_hash.hex()}",
            to_email = os.getenv('EMAIL_TO')
        )
    except Exception as e:
        print(f"Transaction failed: {e}")

        send_email(
            subject="Pray Transaction Failed",
            body=f"Transaction failed with error: {e}",
            to_email = os.getenv('EMAIL_TO')
        )

call_pray()

