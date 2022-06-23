import operator
import unittest

from smtfe import BitVec, Clause, Function, Variable, reset
from smtfe.convert import convert_to_pysmt_formula, convert_to_pysmt_model


class TestModel(unittest.TestCase):
    def setUp(self):
        reset()

    def test_gtl(self):
        a = Variable()
        a > 0
        model = convert_to_pysmt_model()
        # skip the uuid
        self.assertEqual(str(model)[23:], " := 1")

    def test_eq(self):
        a = Variable()
        a == 0
        model = convert_to_pysmt_model()
        self.assertEqual(str(model)[23:], " := 0")

    def test_multiple_clauses(self):
        a = Variable()
        a * 2 == 7
        model = convert_to_pysmt_model()
        self.assertIsNone(model)

    def test_multiple_variables(self):
        a = Variable()
        b = Variable()
        a + 2 * b == 7
        model = convert_to_pysmt_model()
        self.assertEqual(
            str(model),
            f"{b._symbol.symbol_name()} := 0\n{a._symbol.symbol_name()} := 7",
        )

    def test_multiple_statements(self):
        a = Variable()
        b = Variable()

        a > 2
        b < 10
        a + 2 * b == 7
        model = convert_to_pysmt_model()
        self.assertEqual(
            str(model),
            f"{b._symbol.symbol_name()} := 0\n{a._symbol.symbol_name()} := 7",
        )

    def test_demorgan(self):
        a = Variable("a")
        b = Variable("b")
        self.assertEqual(a.name, "a")

        (a & b) == (~((~a) | (~b)))

        model = convert_to_pysmt_model()
        self.assertEqual(str(model), "b := True\na := True")

        ~(a | b) == (~a) | (~b)

        model = convert_to_pysmt_model()
        self.assertEqual(str(model), "b := True\na := True")

        ~(a & b) == (~a) & (~b)

        model = convert_to_pysmt_model()
        self.assertEqual(str(model), "b := False\na := False")

    def test_demorgan_function(self):
        a = Variable("a")
        b = Variable("b")

        @Function.wrap
        def demorgan():
            return (a & b) == (~((~a) | (~b)))

        model = convert_to_pysmt_model()
        self.assertEqual(str(model), "b := True\na := True")

    def test_bitvec(self):
        # https://stackoverflow.com/questions/7165118/assign-value-to-a-bitvector-smtlib2-z3/7165324#7165324
        myu32 = BitVec("myu32", 32)

        myu32 == 0x0000000A

        model = convert_to_pysmt_model()
        self.assertEqual(str(model), "myu32 := 10_32")
