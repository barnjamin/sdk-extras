from algosdk.transaction import assign_group_id
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import encoding
from base64 import b64decode

from sandbox import get_accounts

with open("../logic.teal", "r") as f:
    program = f.read().strip()


client = algod.AlgodClient("a"*64, "http://127.0.0.1:4001")

accts = get_accounts()
acct = accts[0]

sp = client.suggested_params()

res = client.compile(program)
lsa = transaction.LogicSigAccount(b64decode(res['result']))

pay_txn = transaction.PaymentTxn(acct[0], sp, lsa.address(), 10000)
app_txn = transaction.ApplicationCallTxn(acct[0], sp, 2, transaction.OnComplete.NoOpOC, accounts=[accts[2][0]], foreign_assets=[11])
logic_txn = transaction.PaymentTxn(lsa.address(), sp, acct[0], 10000)

assign_group_id([pay_txn, app_txn, logic_txn])

spay_txn = pay_txn.sign(acct[1])
sapp_txn = app_txn.sign(acct[1])
slogic_txn = transaction.LogicSigTransaction(logic_txn, lsa)

drr = transaction.create_dryrun(client, [spay_txn, sapp_txn, slogic_txn])

filename = "py-drr.msgp"
with open(filename, "wb") as f:
    import base64
    f.write(base64.b64decode(encoding.msgpack_encode(drr)))
print(f"Wrote {filename}")
