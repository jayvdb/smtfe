from .variable import InstanceRegistry, function_, Clause


class Function(Clause, InstanceRegistry):
    def __init__(self, name, func):
        self.name = name
        self._symbol = None
        self.operator = function_
        self.other = None
        self.func = func
        self._clauses = None

    @staticmethod
    def wrap(func):
        rv = Function(func.__name__, func)
        return rv

    def __call__(self):
        self.clauses
        return self

    @property
    def clauses(self):
        if self._clauses is None:
            self._clauses = [self.func()]
        return self._clauses

    @property
    def this(self):
        if self._clauses is None:
            self._clauses = [self.func()]
        return self._clauses[0]
