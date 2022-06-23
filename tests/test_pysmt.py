import unittest

from pysmt.shortcuts import (
    Symbol,
    And,
    GE,
    GT,
    LT,
    Plus,
    Equals,
    Int,
    get_model,
    is_sat,
)
from pysmt.typing import INT, BVType


class TestPySMT(unittest.TestCase):
    def test_gt(self):
        a = Symbol("qq", INT)
        f = GT(a, Int(0))
        res = is_sat(f)
        self.assertIs(res, True)
        model = get_model(f)
        self.assertEqual(str(model), "qq := 1")

    def test_bv(self):
        myu32 = Symbol("qp", BVType(32))

        init = myu32.Equals(0x0000000A)

        model = get_model(init)
        self.assertEqual(str(model), "qp := 10_32")
