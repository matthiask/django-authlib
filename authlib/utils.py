""""
NOTE! Please do not depend upon any utilities in this file. Utilities are
added, modified and dropped without prior notice. This file is only for
internal use.

Of course you may always copy the code somewhere else if you like it
(according to the very permissive license of course).
"""

from functools import wraps


def positional(count):
    """
    Only allows ``count`` positional arguments to the decorated callable

    Will be removed as soon as we drop support for Python 2.
    """

    def _dec(fn):
        @wraps(fn)
        def _fn(*args, **kwargs):
            if len(args) > count:
                raise TypeError(
                    "Only %s positional argument%s allowed"
                    % (count, "" if count == 1 else "s")
                )
            return fn(*args, **kwargs)

        return _fn

    return _dec
