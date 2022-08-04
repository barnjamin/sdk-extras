from typing import Iterable
from pyteal import *

class SerializedExpr:
    def __init__(self, name: str, args: list["SerializedExpr"]):
        self.name = name
        self.args = args 
    
    @staticmethod
    def from_expr(e: Expr)->"SerializedExpr":
        nested_args = []

        if hasattr(e, 'args'):
            for x in e.args:
                if isinstance(x, Iterable):
                    for y in x:
                        nested_args.append(SerializedExpr.from_expr(y))
                elif hasattr(x, 'args'):
                    for y in x.args:
                        nested_args.append(SerializedExpr.from_expr(y))
                elif hasattr(x, 'cond'):
                    nested_args.append(SerializedExpr.from_expr(x.cond))
                elif hasattr(x, 'success'):
                    nested_args.append(SerializedExpr.from_expr(x.success))
                else:
                    nested_args.append(SerializedExpr.from_expr(str(x)))
        if hasattr(e, 'arg'):
            nested_args.append(SerializedExpr.from_expr(e.arg))
        if hasattr(e, 'value'):
            nested_args.append(SerializedExpr.from_expr(e.value))
        if hasattr(e, 'success'):
            nested_args.append(SerializedExpr.from_expr(e.success))
        if hasattr(e, 'argLeft') and hasattr(e, 'argRight'):
            nested_args.append(SerializedExpr.from_expr(e.argLeft))
            nested_args.append(SerializedExpr.from_expr(e.argRight))
        if hasattr(e, 'field'):
            nested_args.append(SerializedExpr.from_expr(e.field))
        if hasattr(e, 'methodName'):
            nested_args.append(SerializedExpr.from_expr(e.methodName))
        if hasattr(e, 'slot'):
            nested_args.append(SerializedExpr.from_expr(e.slot))

        name = ""
        if hasattr(e, 'op'):
            name = str(e.op)
        elif len(nested_args) == 0:
            if type(e) is tuple:
                name = e[1]
            else:
                name = str(e)
        
        if name == "":
            name = e.__class__.__name__

        return SerializedExpr(name, nested_args)

    def dictify(self)->dict:
        return {
            "name":self.name,
            "args":[a.dictify() for a in self.args]
        }
