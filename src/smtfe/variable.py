import functools
import operator
import string
import sys

from weakref import WeakSet

import shortuuid

PY35 = sys.version_info >= (3, 5)

shortuuid.set_alphabet(string.ascii_letters)


def function_():
    pass


class Clause:
    def __init__(self, this, operator, other=None):
        assert not isinstance(other, tuple)
        assert not isinstance(this, tuple)
        self.this = this
        self.operator = operator
        self.other = other

    def _find_variable(self):
        if isinstance(self.this, Variable):
            return self.this
        return self.this._find_variable()

    def apply(self, operator, other):
        var = self._find_variable()
        var._remove_sub_clause(self)
        clause = Clause(self, operator, other)
        if isinstance(other, Clause):
            var._remove_sub_clause(other)
            if isinstance(other.this, Variable):
                other.this._remove_sub_clause(other)
        var.clauses.append(clause)
        return clause

    apply_right = apply

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self.this)}, {self.operator}, {str(self.other)})"


class InstanceRegistry:
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        if "instances" not in cls.__dict__:
            cls.instances = WeakSet()
        cls.instances.add(instance)
        return instance

    @classmethod
    def reset(cls):
        if "instances" in cls.__dict__:
            for instance in cls.instances:
                del instance
        cls.instances = WeakSet()


def left_op(operator, comparison=False, identity=None):
    @functools.wraps(operator)
    def wrapper(self, other=None):
        return self.apply(operator, other)

    return wrapper


def right_op(operator):
    @functools.wraps(operator)
    def wrapper(self, other=None):
        return self.apply_right(operator, other)

    return wrapper


class Variable(InstanceRegistry):
    def __init__(self, name=None):
        self.clauses = []
        self._symbol = None
        if name:
            self.name = name
        else:
            self.name = shortuuid.uuid()

    def __repr__(self):
        return f"Variable({id(self)})"

    def _remove_sub_clause(self, sub_clause: Clause):
        self.clauses = [
            clause for clause in list(self.clauses) if repr(clause) != repr(sub_clause)
        ]

    def apply(self, operator, other):
        clause = Clause(self, operator, other)
        if isinstance(other, Clause):
            self._remove_sub_clause(other)
            if isinstance(other, Clause):
                var = other._find_variable()
                var._remove_sub_clause(other)
        self.clauses.append(clause)
        return clause

    apply_right = apply


setattr(Variable, "__add__", left_op(operator.add))
setattr(Variable, "__sub__", left_op(operator.sub))
setattr(Variable, "__mul__", left_op(operator.mul))
setattr(Variable, "__floordiv__", left_op(operator.floordiv))
setattr(Variable, "__truediv__", left_op(operator.truediv))
setattr(Variable, "__mod__", left_op(operator.mod))
setattr(Variable, "__and__", left_op(operator.and_))
setattr(Variable, "__or__", left_op(operator.or_))
setattr(Variable, "__xor__", left_op(operator.xor))
setattr(Variable, "__lshift__", left_op(operator.lshift))
setattr(Variable, "__rshift__", left_op(operator.rshift))

setattr(Variable, "__eq__", left_op(operator.eq, comparison=True))
setattr(Variable, "__ne__", left_op(operator.ne, comparison=True))
setattr(Variable, "__lt__", left_op(operator.lt, comparison=True))
setattr(Variable, "__le__", left_op(operator.le, comparison=True))
setattr(Variable, "__gt__", left_op(operator.gt, comparison=True))
setattr(Variable, "__ge__", left_op(operator.ge, comparison=True))

setattr(Variable, "__radd__", right_op(operator.add))
setattr(Variable, "__rsub__", right_op(operator.sub))
setattr(Variable, "__rmul__", right_op(operator.mul))
setattr(Variable, "__rfloordiv__", right_op(operator.floordiv))
setattr(Variable, "__rtruediv__", right_op(operator.truediv))
setattr(Variable, "__rmod__", right_op(operator.mod))
setattr(Variable, "__rand__", right_op(operator.and_))
setattr(Variable, "__ror__", right_op(operator.or_))
setattr(Variable, "__rxor__", right_op(operator.xor))
setattr(Variable, "__rlshift__", right_op(operator.lshift))
setattr(Variable, "__rrshift__", right_op(operator.rshift))

setattr(Variable, "__invert__", right_op(operator.invert))

if PY35:
    setattr(Variable, "__matmul__", left_op(operator.matmul))
    setattr(Variable, "__rmatmul__", right_op(operator.matmul))


setattr(Clause, "__add__", left_op(operator.add))
setattr(Clause, "__sub__", left_op(operator.sub))
setattr(Clause, "__mul__", left_op(operator.mul))
setattr(Clause, "__floordiv__", left_op(operator.floordiv))
setattr(Clause, "__truediv__", left_op(operator.truediv))
setattr(Clause, "__mod__", left_op(operator.mod))
setattr(Clause, "__and__", left_op(operator.and_))
setattr(Clause, "__or__", left_op(operator.or_))
setattr(Clause, "__xor__", left_op(operator.xor))
setattr(Clause, "__lshift__", left_op(operator.lshift))
setattr(Clause, "__rshift__", left_op(operator.rshift))

setattr(Clause, "__eq__", left_op(operator.eq, comparison=True))
setattr(Clause, "__ne__", left_op(operator.ne, comparison=True))
setattr(Clause, "__lt__", left_op(operator.lt, comparison=True))
setattr(Clause, "__le__", left_op(operator.le, comparison=True))
setattr(Clause, "__gt__", left_op(operator.gt, comparison=True))
setattr(Clause, "__ge__", left_op(operator.ge, comparison=True))

setattr(Clause, "__radd__", right_op(operator.add))
setattr(Clause, "__rsub__", right_op(operator.sub))
setattr(Clause, "__rmul__", right_op(operator.mul))
setattr(Clause, "__rfloordiv__", right_op(operator.floordiv))
setattr(Clause, "__rtruediv__", right_op(operator.truediv))
setattr(Clause, "__rmod__", right_op(operator.mod))
setattr(Clause, "__rand__", right_op(operator.and_))
setattr(Clause, "__ror__", right_op(operator.or_))
setattr(Clause, "__rxor__", right_op(operator.xor))
setattr(Clause, "__rlshift__", right_op(operator.lshift))
setattr(Clause, "__rrshift__", right_op(operator.rshift))

setattr(Clause, "__invert__", right_op(operator.invert))

if PY35:
    setattr(Clause, "__matmul__", left_op(operator.matmul))
    setattr(Clause, "__rmatmul__", right_op(operator.matmul))
