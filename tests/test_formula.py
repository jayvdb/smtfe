import operator
import unittest

from smtfe import BitVec, Clause, Function, Variable, reset
from smtfe.convert import convert_to_pysmt_formula, join_formula
from smtfe.utils import get_formula, emit_smt2


class TestFormula(unittest.TestCase):
    def setUp(self):
        reset()

    def test_gt(self):
        a = Variable()
        a > 0
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[1].symbol_name()
        self.assertEqual(repr(f), f"(0 < {a_uuid})")

    def test_eq(self):
        a = Variable()
        a == 0
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[0].symbol_name()
        self.assertEqual(repr(f), f"({a_uuid} = 0)")

    def test_multiple_clauses(self):
        a = Variable()
        a * 2 == 7
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[0].args()[0].symbol_name()
        self.assertEqual(repr(f), f"(({a_uuid} * 2) = 7)")

        a = Variable()
        7 == a * 2
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[0].args()[0].symbol_name()
        self.assertEqual(repr(f), f"(({a_uuid} * 2) = 7)")

    def test_multiple_variables(self):
        a = Variable()
        b = Variable()
        a + 2 * b == 7
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[0].args()[0].symbol_name()
        b_uuid = f.args()[0].args()[1].args()[0].symbol_name()
        self.assertEqual(repr(f), f"(({a_uuid} + ({b_uuid} * 2)) = 7)")

    def test_multiple_statements(self):
        a = Variable()
        b = Variable()

        a > 2
        f = convert_to_pysmt_formula(a.clauses[0])
        a_uuid = f.args()[1].symbol_name()
        self.assertEqual(repr(f), f"(2 < {a_uuid})")

        b < 10
        f = convert_to_pysmt_formula(b.clauses[0])
        b_uuid = f.args()[0].symbol_name()
        self.assertEqual(repr(f), f"({b_uuid} < 10)")

        a + 2 * b == 7
        f = convert_to_pysmt_formula(a.clauses[1])
        self.assertEqual(repr(f), f"(({a_uuid} + ({b_uuid} * 2)) = 7)")

        self.assertEqual(len(b.clauses), 1)

        f = join_formula(a.clauses)
        self.assertEqual(
            repr(f), f"((2 < {a_uuid}) & (({a_uuid} + ({b_uuid} * 2)) = 7))"
        )

        f = join_formula(b.clauses)
        self.assertEqual(repr(f), f"({b_uuid} < 10)")

        f = join_formula(a.clauses + b.clauses)
        self.assertEqual(
            f.serialize(100),
            f"((2 < {a_uuid}) & ((({a_uuid} + ({b_uuid} * 2)) = 7) & ({b_uuid} < 10)))",
        )

    def test_demorgan(self):
        a = Variable("a")
        b = Variable("b")
        self.assertEqual(a.name, "a")

        (a & b) == (~((~a) | (~b)))

        f = join_formula(a.clauses + b.clauses)
        self.assertEqual(f.serialize(100), f"((b & a) <-> (! ((! a) | (! b))))")

    def test_ingest_demorgan(self):
        s = """(declare-const a Bool)
(declare-const b Bool)


(define-fun demorgan ()  Bool
  (= (and a b) (not (or (not a) (not b)))))


(assert demorgan)
(check-sat)
(get-value (a b))"""
        f = get_formula(s)
        self.assertIsNotNone(f)

    def test_demorgan_function(self):
        a = Variable("a")
        b = Variable("b")

        @Function.wrap
        def demorgan():
            return (a & b) == (~((~a) | (~b)))

        # demorgan()

        f = join_formula([demorgan])
        print(emit_smt2(f))
        self.assertIn(
            f.serialize(100),
            [
                "(demorgan(a, b) <-> ((b & a) <-> (! ((! a) | (! b)))))",
                "(demorgan(b, a) <-> ((b & a) <-> (! ((! a) | (! b)))))",
            ],
        )

    def test_bitvec(self):
        # https://stackoverflow.com/questions/7165118/assign-value-to-a-bitvector-smtlib2-z3/7165324#7165324
        myu32 = BitVec("myu32", 32)

        myu32 == 0x0000000A

        self.assertEqual(repr(myu32.clauses), repr([Clause(myu32, operator.eq, 10)]))
