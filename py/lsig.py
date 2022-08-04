import os
import base64
import json

from algosdk.v2client import algod
from algosdk.future.transaction import *

# Read a file
def load_resource(res):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    with open(path, "r") as f:
        data = f.read()
    return data


def contract_account_example():
    # Create an algod client, using default sandbox parameters here
    algod_token = "a" * 64
    algod_address = "http://localhost:4001" 
    algod_client = algod.AlgodClient(algod_token, algod_address)        


    # Load in our program
    myprogram = "sample.teal"
    data = load_resource(myprogram)

    # Compile the program against the algod
    response = algod_client.compile(data)
    print(f"Response Result (base64 encoded): {response['result']}")
    print(f"Response Hash: {response['hash']}")

    # Decode the program to bytes and encode the argument as bytes
    program = base64.b64decode(response['result'])
    arg1 = (123).to_bytes(8, 'big')

    # Create the lsig account, passing arg
    lsig = LogicSigAccount(program, args=[arg1])
    sender = lsig.address()
    print(f"Address of lsig: {sender}")

    # Get suggested parameters
    params = algod_client.suggested_params()

    # replace with any other address or amount
    receiver = "J4F3VSXCSSEFV74N2NANUTMJ7GXP62H5J2PJFBHPCH42WLN4K7RS5HEL6Y"
    amount = 10000 

    # Create a transaction
    txn = PaymentTxn(sender, params, receiver, amount)

    # Create the LogicSigTransaction with contract account LogicSigAccount
    lstx = transaction.LogicSigTransaction(txn, lsig.lsig)

    # Send raw LogicSigTransaction to network
    txid = algod_client.send_transaction(lstx)
    print("Transaction ID: " + txid) 

    # wait for confirmation 
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    print(f"Result confirmed in round: {confirmed_txn['confirmed-round']}")
    print(f"Transaction information: {json.dumps(confirmed_txn, indent=4)}")

contract_account_example()