from algosdk.transaction import assign_group_id
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import encoding
from base64 import b64decode

from sandbox import get_accounts

client = algod.AlgodClient("a" * 64, "http://127.0.0.1:4001")

accts = get_accounts()
(addr1, pk1) = accts[0]
(addr2, pk2) = accts[1]

sp = client.suggested_params()

pay_txn = transaction.PaymentTxn(addr1, sp, addr2, 0, close_remainder_to=addr2)
pay_txn.receiver = encoding.encode_address(bytes(32) )
with open("pay.txn", "w") as f:
    f.write(encoding.msgpack_encode(pay_txn))

#spay_txn = pay_txn.sign(pk1)
#with open("signed_pay.txn", "w") as f:
#    f.write(encoding.msgpack_encode(spay_txn))
#
#
#with open("pay.txn", "r") as f:
#    recovered_txn = encoding.future_msgpack_decode(f.read())
#
#print(recovered_txn)
#
#with open("signed_pay.txn", "r") as f:
#    recovered_signed_txn = encoding.future_msgpack_decode(f.read())
#
#print(recovered_signed_txn)

# app_txn = transaction.ApplicationCallTxn(acct[0], sp, 1, transaction.OnComplete.NoOpOC, accounts=[accts[2][0]])
# logic_txn = transaction.PaymentTxn(lsa.address(), sp, acct[0], 10000)
#
# assign_group_id([pay_txn, app_txn, logic_txn])
#
# spay_txn = pay_txn.sign(acct[1])
# sapp_txn = app_txn.sign(acct[1])
# slogic_txn = transaction.LogicSigTransaction(logic_txn, lsa)
#
# drr = transaction.create_dryrun(client, [spay_txn, sapp_txn, slogic_txn])
#
# filename = "py-drr.msgp"
# with open(filename, "wb") as f:
#    import base64
#    f.write(base64.b64decode(encoding.msgpack_encode(drr)))
# print(f"Wrote {filename}")
#
