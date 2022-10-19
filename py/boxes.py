import base64
from algosdk import *

sk, addr = account.generate_account()
print(addr, sk)


client = v2client.algod.AlgodClient("a"*64, "http://localhost:4001")
sp = client.suggested_params()

txn = future.transaction.ApplicationCallTxn(addr, sp, 123, future.transaction.OnComplete.NoOpOC, boxes=[[123, "my box"]])
with open("single-box-app-call.txn", "wb") as f:
    f.write(base64.b64decode(encoding.msgpack_encode(txn)))

txn = future.transaction.ApplicationCallTxn(addr, sp, 123, future.transaction.OnComplete.NoOpOC, boxes=[[123, "my box"], [456, "my other box"]], foreign_apps=[456])
with open("multi-box-app-call.txn", "wb") as f:
    f.write(base64.b64decode(encoding.msgpack_encode(txn)))

#txn = future.transaction.ApplicationCallTxn(addr, sp, 123, future.transaction.OnComplete.NoOpOC, boxes=[[123, "my box"], [456, "my other box"]], foreign_apps=[456])
#with open("multi-box-app-call.txn", "wb") as f:
#    f.write(base64.b64decode(encoding.msgpack_encode(txn)))