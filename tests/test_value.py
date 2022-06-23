import operator
import unittest

import pysmt.operators as op
from pysmt.fnode import FNode

from smtfe import BitVec, Clause, Variable, reset
from smtfe.convert import get_values, get_value_str


class TestValue(unittest.TestCase):
    def setUp(self):
        reset()

    def test_gtl(self):
        a = Variable()
        a > 0
        values = get_values((a,))
        self.assertCountEqual(values, {a._symbol: 1})
        s = get_value_str((a,))
        self.assertCountEqual(s, f"(({a._symbol.symbol_name()} 1))")

    def test_eq(self):
        a = Variable()
        a == 0
        values = get_values((a,))
        self.assertCountEqual(values, {a._symbol: 0})
        s = get_value_str((a,))
        self.assertCountEqual(s, f"(({a._symbol.symbol_name()} 0))")

    def test_multiple_clauses(self):
        a = Variable()
        a * 2 == 7
        values = get_values((a,))
        self.assertCountEqual(values, {})
        s = get_value_str((a,))
        self.assertCountEqual(s, f"")

    def test_multiple_variables(self):
        a = Variable()
        b = Variable()
        a + 2 * b == 7
        values = get_values((a, b))
        self.assertCountEqual(values, {a._symbol: 7, b._symbol: 0})
        s = get_value_str((a, b))
        self.assertCountEqual(
            s, f"(({a._symbol.symbol_name()} 7)\n ({b._symbol.symbol_name()} 0))"
        )

    def test_multiple_statements(self):
        a = Variable()
        b = Variable()

        a > 2
        b < 10
        a + 2 * b == 7
        values = get_values((a, b))
        self.assertCountEqual(values, {a._symbol: 7, b._symbol: 0})
        s = get_value_str((a, b))
        self.assertCountEqual(
            s, f"(({a._symbol.symbol_name()} 7)\n ({b._symbol.symbol_name()} 0))"
        )

    def test_bitvec(self):
        myu32 = BitVec("myu32", 32)

        myu32 == 0x0000000A

        values = get_values((myu32,))
        self.assertEqual(repr(values), "{" + str(myu32._symbol) + ": 10_32}")
        value = values[myu32._symbol]
        self.assertIsInstance(value, FNode)
        self.assertEqual(value._content.node_type, op.BV_CONSTANT)

        s = get_value_str((myu32,))
        self.assertEqual(s, "((" + str(myu32._symbol) + " #x0000000a))")
