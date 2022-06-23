import io

from pysmt.smtlib.parser.parser import SmtLibParser
from pysmt.smtlib.script import smtlibscript_from_formula


def emit_smt2(f):
    script = smtlibscript_from_formula(f)
    fh = io.StringIO()
    script.serialize(fh)
    return fh.getvalue()


def get_formula(s):
    fh = io.StringIO(s)
    script = SmtLibParser().get_script(fh)
    return script.get_strict_formula()
