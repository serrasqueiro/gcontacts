# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Debug facilities

Author: Henrique Moreira
"""

DEBUG = 0

def dprint(*args, **kwargs):
    dbg = kwargs.pop("debug", None)
    if dbg is None:
        if DEBUG <= 0:
            return False
    else:
        if dbg <= 0:
            return False
    print(*args, **kwargs)
    return True
