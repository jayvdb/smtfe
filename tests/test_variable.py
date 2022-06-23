import operator
import unittest

from smtfe import BitVec, Clause, Function, Variable, reset


class TestVariable(unittest.TestCase):
    def setUp(self):
        reset()

    def test_instances(self):
        self.assertEqual(len(Variable.instances), 0)
        a = Variable()
        b = Variable()
        instances = list(Variable.instances)
        self.assertEqual(len(instances), 2)
        self.assertCountEqual(instances, [a, b])

    def test_gt(self):
        a = Variable()
        a > 0
        self.assertEqual(repr(a.clauses), repr([Clause(a, operator.gt, 0)]))

    def test_eq(self):
        a = Variable()
        a == 0
        self.assertEqual(repr(a.clauses), repr([Clause(a, operator.eq, 0)]))

    def test_python_reduction(self):
        a = Variable()
        a == 3 * 2
        self.assertEqual(
            repr(a.clauses), repr([Clause(a, operator.eq, 6)])
        )  # 3 * 2 already reduced to 6 by Python
        a = Variable()
        a == 0 * 2
        self.assertEqual(
            repr(a.clauses), repr([Clause(a, operator.eq, 0)])
        )  # 0 * 2 already reduced to 0 by Python

    def test_multiple_clauses(self):
        a = Variable()
        a * 2 == 7
        self.assertEqual(
            repr(a.clauses), repr([Clause(Clause(a, operator.mul, 2), operator.eq, 7)])
        )
        a = Variable()
        7 == a * 2
        self.assertEqual(
            repr(a.clauses), repr([Clause(Clause(a, operator.mul, 2), operator.eq, 7)])
        )

    def test_multiple_variables(self):
        a = Variable()
        b = Variable()
        a + 2 * b == 7
        self.assertEqual(
            repr(a.clauses),
            repr(
                [
                    Clause(
                        Clause(a, operator.add, Clause(b, operator.mul, 2)),
                        operator.eq,
                        7,
                    )
                ]
            ),
        )
        self.assertEqual(repr(b.clauses), repr([]))

    def test_multiple_statements(self):
        a = Variable()
        b = Variable()
        a > 2
        b < 10
        self.assertEqual(repr(a.clauses), repr([Clause(a, operator.gt, 2)]))
        self.assertEqual(repr(b.clauses), repr([Clause(b, operator.lt, 10)]))
        a + 2 * b == 7
        self.assertEqual(
            repr(a.clauses),
            repr(
                [
                    Clause(a, operator.gt, 2),
                    Clause(
                        Clause(a, operator.add, Clause(b, operator.mul, 2)),
                        operator.eq,
                        7,
                    ),
                ]
            ),
        )
        self.assertEqual(
            repr(b.clauses),
            repr(
                [
                    Clause(b, operator.lt, 10),
                ]
            ),
        )

    def test_demorgan(self):
        a = Variable("a")
        b = Variable("b")
        self.assertEqual(a.name, "a")
        (a & b) == (~((~a) | (~b)))
        self.assertEqual(
            repr(a.clauses),
            repr(
                [
                    Clause(
                        Clause(a, operator.and_, b),
                        operator.eq,
                        Clause(
                            Clause(
                                Clause(a, operator.invert, None),
                                operator.or_,
                                Clause(b, operator.invert, None),
                            ),
                            operator.invert,
                            None,
                        ),
                    )
                ]
            ),
        )
        self.assertEqual(repr(b.clauses), "[]")

    def test_demorgan_function(self):
        a = Variable("a")
        b = Variable("b")

        @Function.wrap
        def demorgan():
            return (a & b) == (~((~a) | (~b)))

        demorgan()

        self.assertEqual(
            repr(a.clauses),
            repr(
                [
                    Clause(
                        Clause(a, operator.and_, b),
                        operator.eq,
                        Clause(
                            Clause(
                                Clause(a, operator.invert, None),
                                operator.or_,
                                Clause(b, operator.invert, None),
                            ),
                            operator.invert,
                            None,
                        ),
                    )
                ]
            ),
        )
        self.assertEqual(repr(b.clauses), "[]")

    def test_bitvec(self):
        myu32: BitVec[32] = BitVec("myu32", 32)

        myu32 == 0x0000000A

        self.assertEqual(repr(myu32.clauses), repr([Clause(myu32, operator.eq, 10)]))
