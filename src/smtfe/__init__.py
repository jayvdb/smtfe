from .variable import Clause, Variable
from .function import Function
from .bitvec import BitVec
from .convert import (
    convert_to_pysmt_model as _convert_to_pysmt_model,
    _reset as _convert_reset,
    get_value_str,
)


def reset():
    Variable.reset()
    BitVec.reset()
    Function.reset()
    _convert_reset()


def check_sat():
    rv = _convert_to_pysmt_model()
    if rv:
        print("sat")
    else:
        print("unsat")


def get_model(*args, **kwargs):
    return _convert_to_pysmt_model()


def get_value(args: tuple):
    print(get_value_str(args))
