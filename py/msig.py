from algosdk.future import transaction
from algosdk.v2client import algod
from sandbox import get_accounts


client = algod.AlgodClient("a"*64, "http://localhost:4001")

accts = get_accounts()
addr1, pk1 = accts[0]
addr2, pk2 = accts[1]
addr3, pk3 = accts[2]

msig = transaction.Multisig(1, 2, [addr1, addr2, addr3])

sp =  client.suggested_params()

#funder = transaction.PaymentTxn(addr1, sp, msig.address(), 10000000)
#client.send_transaction(funder.sign(pk1))

ptxn = transaction.PaymentTxn(msig.address(), sp, addr2, 10000, note="x")
ptxn2 = transaction.PaymentTxn(msig.address(), sp, addr2, 10000, note="y")

transaction.assign_group_id([ptxn, ptxn2])

test = transaction.MultisigTransaction(ptxn, msig.get_multisig_account())
test.sign(pk1)
test.sign(pk2)

test2 = transaction.MultisigTransaction(ptxn2, msig.get_multisig_account())
test2.sign(pk1)
test2.sign(pk2)

txid = client.send_transactions([test, test2]) 
print(f"Sent {txid}")
result = transaction.wait_for_confirmation(client, txid)
print(f"result: {result}")
