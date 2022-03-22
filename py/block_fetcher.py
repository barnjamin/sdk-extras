from algosdk.v2client import algod
from algosdk import encoding
from algosdk.future import transaction
import msgpack
import base64

sandbox = True

token = ""
host = "https://node.algoexplorerapi.io"

if sandbox:
    token = "a" * 64
    host = "http://localhost:4001"

client = algod.AlgodClient(token, host)


def fetch_block(round: int):
    block = client.block_info(round, response_format="msgpack")
    dblock = msgpack.unpackb(block, raw=True, strict_map_key=False)

    raw_block = dblock[b"block"]
    if b"txns" not in raw_block:
        return

    gh = raw_block[b"gh"]
    gen = raw_block[b"gen"].decode("utf-8")

    for stxn in raw_block[b"txns"]:
        txn = parse_transaction_msgp(stxn[b"txn"], gh, gen)
        # TODO: Check if relevant transaction w/ receiver/txn type

        print(txn.get_txid())

        inner_txns = parse_inners_msgp(stxn)
        if len(inner_txns) > 0:
            print_ids_recursive(txn, inner_txns, 0)


def parse_inners_msgp(stxn):
    parsed = []

    if b"dt" not in stxn or b"itx" not in stxn[b"dt"]:
        return parsed

    itxns = stxn[b"dt"][b"itx"]
    for idx in range(len(itxns)):
        itxn = itxns[idx][b"txn"]
        t = {"gh": b"", "gen": "", **{k.decode("utf-8"): v for (k, v) in itxn.items()}}
        parsed.append(
            (encoding.future_msgpack_decode(t), parse_inners_msgp(itxns[idx]))
        )

    return parsed


def parse_transaction_msgp(
    txn: transaction.Transaction, gh: bytes, gen: str
) -> transaction.Transaction:
    t = {"gh": gh, "gen": gen, **{k.decode("utf-8"): v for (k, v) in txn.items()}}
    return encoding.future_msgpack_decode(t)


def print_ids_recursive(txn, inner_txns, level):
    for idx in range(len(inner_txns)):
        (itxn, inners) = inner_txns[idx]

        print("{}{}".format("\t" * (level + 1), get_itxn_id(itxn, txn, idx)))
        if len(inners) > 0:
            print_ids_recursive(itxn, inners, level + 1)


def get_itxn_id(
    itxn: transaction.Transaction, caller: transaction.Transaction, idx: int
) -> str:
    input = b"TX" + txid_to_bytes(caller.get_txid())
    input += idx.to_bytes(8, "big")
    input += base64.b64decode(encoding.msgpack_encode(itxn))
    return bytes_to_txid(encoding.checksum(input))


def txid_to_bytes(txid):
    return base64.b32decode(encoding._correct_padding(txid))


def bytes_to_txid(b):
    return base64.b32encode(b).strip(b"=").decode("utf-8")


if __name__ == "__main__":
    n = 100
    status = client.status()
    last_n = max(status["last-round"] - n, 0)
    for i in range(n):
        fetch_block(last_n + i)
