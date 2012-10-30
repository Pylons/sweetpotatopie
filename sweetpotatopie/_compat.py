import sys

PY3 = sys.version_info[0] == 3

if PY3: # pragma: no cover
    text_type = str
    from io import StringIO
else: # pragma: no cover
    text_type = unicode
    from StringIO import StringIO

def u(x):
    return text_type(x)
