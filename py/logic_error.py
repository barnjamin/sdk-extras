import re
from inspect import currentframe, getframeinfo
import base64
from pyteal import *
from algosdk.source_map import SourceMap
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from sandbox import get_accounts

LOGIC_ERROR = "TransactionPool.Remember: transaction ([A-Z0-9]+): logic eval error: (.*). Details: pc=([0-9]+), opcodes=.*"


def parse_logic_error(error_str: str) -> tuple[str, str, int]:
    matches = re.match(LOGIC_ERROR, error_str)
    if matches is None:
        return "", "", 0

    txid = matches.group(1)
    msg = matches.group(2)
    pc = int(matches.group(3))

    return txid, msg, pc


def tiny_trace(lines: list[str], line_no: int, num_lines: int) -> str:
    lines[line_no] += "\t\t<-- Error"
    lines_before = max(0, line_no - num_lines)
    lines_after = min(len(lines), line_no + num_lines)
    return "\n\t".join(lines[lines_before:lines_after])


class LogicException(Exception):
    def __init__(
        self,
        logic_error: Exception,
        program: str,
        map: SourceMap,
    ):
        self.logic_error = logic_error
        self.logic_error_str = str(logic_error)

        self.program = program
        self.map = map

        self.lines = program.split("\n")

        self.txid, self.msg, self.pc = parse_logic_error(self.logic_error_str)
        self.line_no = self.map.get_line_for_pc(self.pc)

    def __str__(self):
        return f"Txn {self.txid} had error '{self.msg}' at PC {self.pc} and Source Line {self.line_no}: \n\n\t{self.trace()}"

    def trace(self, lines: int = 5) -> str:
        return tiny_trace(self.lines, self.line_no, lines)

def comment_for_assert(cf)->str:
    finfo = getframeinfo(cf)
    return f"{finfo.filename}:L{finfo.lineno}"

def demo():
    addr, sk = get_accounts().pop()

    client = AlgodClient("a"*64, "http://localhost:4001")

    program = Seq(Assert(Int(0), comment=comment_for_assert(currentframe())), Int(1))
    approval = compileTeal(program, mode=Mode.Application, version=6)

    result = client.compile(approval, source_map=True)
    approval_bin = base64.b64decode(result["result"])
    src_map = SourceMap(result["sourcemap"])

    sp = client.suggested_params()

    schema = transaction.StateSchema(0,0)
    txn = transaction.ApplicationCreateTxn(addr, sp, transaction.OnComplete.NoOpOC, approval_bin, approval_bin, schema, schema)

    try:
        result = client.send_transaction(txn.sign(sk))
    except Exception as e:
        le = LogicException(e, approval, src_map)
        print(f"Assert comment: '{le.lines[le.line_no-1]}'")

if __name__ == "__main__":
    demo()