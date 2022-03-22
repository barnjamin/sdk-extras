from algosdk.v2client import algod
from algosdk import encoding
from algosdk.future import transaction
from typing import List, Dict
import msgpack
import base64

sandbox = False 

token = ""
host = "https://node.algoexplorerapi.io"

if sandbox:
    token = "a" * 64
    host = "http://localhost:4001"

client = algod.AlgodClient(token, host)


def parse_signed_transaction_msgp(
    txn: dict, gh: bytes, gen: str
) -> transaction.Transaction:
    stxn = {
        "txn": {
            "gh": gh,
            "gen": gen,
            **{k.decode("utf-8"): v for (k, v) in txn[b"txn"].items()},
        }
    }
    if b"sig" in txn:
        stxn["sig"] = txn[b"sig"]
    #if b"msig" in txn:
        #stxn["msig"] = {k.decode("utf-8"):v for (k,v) in txn[b"msig"].items()}
    if "lsig" in txn:
        stxn["lsig"] = txn[b"lsig"]
    if b"sgnr" in txn:
        stxn["sgnr"] = txn[b"sgnr"]
    return encoding.future_msgpack_decode(stxn)


class StateDelta:
    action: int
    bytes: bytes
    uint: int

    @staticmethod
    def from_msgp(state_delta: dict) -> "StateDelta":
        sd = StateDelta()
        if b"at" in state_delta:
            sd.action = state_delta[b"at"]
        if b"bs" in state_delta:
            sd.bytes = state_delta[b"bs"]
        if b"ui" in state_delta:
            sd.uint = state_delta[b"ui"]
        return sd


class EvalDelta:
    global_delta: List[StateDelta]
    local_deltas: Dict[int, StateDelta]
    logs: List[str]
    inner_txns: List["SignedTxnWithAD"]

    def __init__(
        self,
        global_delta: StateDelta = None,
        local_deltas: Dict[int, StateDelta] = None,
        logs: List[str] = [],
        inner_txns: List["SignedTxnWithAD"] = [],
    ):
        self.global_delta = global_delta
        self.local_deltas = local_deltas
        self.logs = logs
        self.inner_txns = inner_txns

    @staticmethod
    def from_msgp(delta: dict) -> "EvalDelta":
        ed = EvalDelta()
        if b"gd" in delta:
            ed.global_delta = StateDelta.from_msgp(delta[b"gd"])
        if b"ld" in delta:
            ed.local_deltas = {k: StateDelta.from_msgp(v) for k, v in delta[b"ld"].items()}
        if b"lg" in delta:
            ed.logs = delta[b"lg"]
        if b"itx" in delta:
            ed.inner_txns = [
                SignedTxnWithAD.from_msgp(itxn, b"", "") for itxn in delta[b"itx"]
            ]
        return ed


class ApplyData:
    closing_amount: int
    asset_closing_amount: int
    sender_rewards: int
    receiver_rewards: int
    close_rewards: int
    eval_delta: EvalDelta
    config_asset: int
    application_id: int

    def __init__(
        self,
        closing_amount=0,
        asset_closing_amount=0,
        sender_rewards=0,
        receiver_rewards=0,
        close_rewards=0,
        eval_delta=None,
        config_asset=0,
        application_id=0,
    ):
        self.closing_amount = closing_amount
        self.asset_closing_amount = asset_closing_amount
        self.sender_rewards = sender_rewards
        self.receiver_rewards = receiver_rewards
        self.close_rewards = close_rewards
        self.eval_delta = eval_delta
        self.config_asset = config_asset
        self.application_id = application_id

    @staticmethod
    def from_msgp(apply_data: dict) -> "ApplyData":
        ad = ApplyData()
        if b"ca" in apply_data:
            ad.closing_amount = apply_data[b"ca"]
        if b"aca" in apply_data:
            ad.asset_closing_amount = apply_data[b"aca"]
        if b"rs" in apply_data:
            ad.sender_rewards = apply_data[b"rs"]
        if b"rr" in apply_data:
            ad.receiver_rewards = apply_data[b"rr"]
        if b"rc" in apply_data:
            ad.close_rewards = apply_data[b"rc"]
        if b"caid" in apply_data:
            ad.config_asset = apply_data[b"caid"]
        if b"apid" in apply_data:
            ad.application_id = apply_data[b"apid"]
        if b"dt" in apply_data:
            ad.eval_delta = EvalDelta.from_msgp(apply_data[b"dt"])
        return ad


class SignedTxnWithAD:
    stxn: transaction.SignedTransaction
    ad: ApplyData

    @staticmethod
    def from_msgp(stxn, gh, gen) -> "SignedTxnWithAD":
        s = SignedTxnWithAD()
        if b"txn" in stxn:
            s.stxn = parse_signed_transaction_msgp(stxn, gh, gen)
        s.ad = ApplyData.from_msgp(stxn)
        return s


def fetch_block(round: int):
    block = client.block_info(round, response_format="msgpack")
    dblock = msgpack.unpackb(block, raw=True, strict_map_key=False)

    raw_block = dblock[b"block"]
    if b"txns" not in raw_block:
        return

    gh = raw_block[b"gh"]
    gen = raw_block[b"gen"].decode("utf-8")

    for stxn in raw_block[b"txns"]:
        swad = SignedTxnWithAD.from_msgp(stxn, gh, gen)
        ## TODO: Check if relevant transaction w/ receiver/txn type

        print(swad.stxn.get_txid())

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
