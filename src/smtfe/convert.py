import functools
import operator

import pysmt.operators as op

from pysmt.shortcuts import (
    And,
    Bool,
    BV,
    EqualsOrIff,
    Function,
    get_model,
    GT,
    Int,
    LT,
    Not,
    Or,
    Plus,
    Symbol,
    Times,
)
from pysmt.typing import FunctionType, BOOL, INT, BVType

from .variable import Clause, Variable, function_
from .function import Function as Function_
from .bitvec import BitVec

_variable_symbol_cache = {}


def _reset():
    _variable_symbol_cache.clear()


_operator_smt_mapping = {
    operator.and_: And,
    operator.gt: GT,
    operator.lt: LT,
    operator.eq: EqualsOrIff,
    operator.mul: Times,
    operator.add: Plus,
    operator.or_: Or,
    operator.invert: Not,
    function_: Function,
}

_symbol_smt_mapping = {
    int: INT,
    bool: BOOL,
}
_native_smt_mapping = {
    int: Int,
    bool: Bool,
}


def _operator_to_pysmt(op):
    return _operator_smt_mapping[op]


def _get_symbol(variable, pysmt_symbol_type):
    # TODO: existing symbol should have the same pysmt_type
    if not variable._symbol:
        variable._symbol = Symbol(variable.name, pysmt_symbol_type)
    return variable._symbol


def _derive_py_type(val):
    if val is None:
        return None
    if isinstance(val, Variable):
        return None
    if isinstance(val, Clause):
        py_type = _derive_py_type(val.this)
        if py_type is not None:
            return py_type
        py_type = _derive_py_type(val.other)
        if py_type is not None:
            return py_type
        if val.operator in [operator.and_, operator.or_, operator.invert]:
            return bool
        return None
    return type(val)


def _derive_symbol_type(val):
    py_type = _derive_py_type(val)
    assert py_type
    return _symbol_smt_mapping[py_type]


def _derive_native_type(val):
    py_type = _derive_py_type(val)
    assert py_type
    return _native_smt_mapping[py_type]


def convert_to_pysmt_formula(clause):
    clause_op_pysmt = _operator_to_pysmt(clause.operator)

    if isinstance(clause.this, Variable) and clause.operator in [
        function_,
        operator.invert,
    ]:
        symbol_type_pysmt = _derive_symbol_type(clause)
        this = _get_symbol(clause.this, symbol_type_pysmt)
        return clause_op_pysmt(this)
    elif isinstance(clause.this, Variable) and isinstance(clause.other, Variable):
        symbol_type_pysmt = _derive_symbol_type(clause)
        this = _get_symbol(clause.this, symbol_type_pysmt)
        other = _get_symbol(clause.other, symbol_type_pysmt)
        return clause_op_pysmt(other, this)
    elif isinstance(clause.this, Variable):
        if isinstance(clause.this, BitVec):
            symbol_type_pysmt = BVType(clause.this.bits)
            native_type_pysmt = functools.partial(BV, width=clause.this.bits)
        else:
            symbol_type_pysmt = _derive_symbol_type(clause)
            native_type_pysmt = _derive_native_type(clause)

        this = _get_symbol(clause.this, symbol_type_pysmt)

        if isinstance(clause.other, Clause):
            other = convert_to_pysmt_formula(clause.other)
        else:
            other = native_type_pysmt(clause.other)

        return clause_op_pysmt(this, other)
    elif isinstance(clause.other, Variable):
        if isinstance(clause.other, BitVec):
            symbol_type_pysmt = BVType(clause.other.bits)
            native_type_pysmt = functools.partial(BV, width=clause.other.bits)
        else:
            symbol_type_pysmt = _derive_symbol_type(clause)
            native_type_pysmt = _derive_native_type(clause)

        other = _get_symbol(clause.this, symbol_type_pysmt)

        if isinstance(clause.this, Clause):
            this = convert_to_pysmt_formula(clause.this)
        else:
            this = native_type_pysmt(clause.this)

        return clause_op_pysmt(other, this)
    elif isinstance(clause.this, Clause):
        this = convert_to_pysmt_formula(clause.this)
        if isinstance(clause.other, Clause):
            other = convert_to_pysmt_formula(clause.other)
            return clause_op_pysmt(this, other)
        elif clause.operator == function_:
            vars = sorted(get_variables(clause.this))
            syms = [var._symbol for var in vars]
            func_symbol_type = FunctionType(BOOL, [BOOL, BOOL])
            func_symbol = Symbol(clause.name, func_symbol_type)
            func_node = Function(func_symbol, syms)
            return EqualsOrIff(func_node, this)
        elif clause.operator == operator.invert:
            return clause_op_pysmt(this)
        native_type_pysmt = _derive_native_type(clause.other)
        other = native_type_pysmt(clause.other)
        return clause_op_pysmt(this, other)

    assert False


def get_variables(clause):
    variables = set()
    if isinstance(clause.this, Variable):
        variables.add(clause.this)
    if isinstance(clause.other, Variable):
        variables.add(clause.other)
    if isinstance(clause.this, Clause):
        variables |= get_variables(clause.this)
    if isinstance(clause.other, Clause):
        variables |= get_variables(clause.other)
    return variables


def join_formula(clauses):
    assert clauses
    if len(clauses) == 1:
        return convert_to_pysmt_formula(clauses[0])
    return And(convert_to_pysmt_formula(clauses[0]), join_formula(clauses[1:]))


def convert_to_pysmt_model():
    variables = []
    if hasattr(Variable, "instances"):
        variables += Variable.instances
    if hasattr(BitVec, "instances"):
        variables += BitVec.instances
    clauses = []
    for variable in variables:
        clauses += variable.clauses
    if hasattr(Function_, "instances"):
        for instance in Function_.instances:
            clauses += instance.clauses
    if len(clauses) == 1:
        return get_model(convert_to_pysmt_formula(clauses[0]))
    f = join_formula(clauses)
    return get_model(f)


def get_values(args: tuple):
    model = convert_to_pysmt_model()
    try:
        return dict(model)
    except TypeError:
        return {}


def get_value_str(args: tuple):
    values = get_values(args)
    if not values:
        return ""
    s = []
    symbols = sorted(values.keys(), key=lambda x: x._content)
    for symbol in symbols:
        value = values[symbol]
        if value._content.node_type == op.BV_CONSTANT:
            # See https://github.com/pysmt/pysmt/issues/548
            padding = 10
            res = "#" + f"{value.constant_value():#0{padding}x}"[1:]
            s.append(f"({symbol.symbol_name()} {res})")
        else:
            s.append(f"({symbol.symbol_name()} {value})")
    if len(s) == 1:
        return f"({s[0]})"
    return "(" + "\n ".join(s) + ")"
