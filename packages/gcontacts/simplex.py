# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" simplex -- basic keying for google contacts

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring


import hashlib
from gcontacts.simplifier import simpler_words
from gcontacts.dprint import dprint

def simplex(astr:str) -> str:
    """ Returns a simpler wording for easier hashing """
    res = simpler_field(simpler_words(astr)).upper()
    for etc in "_()[]{}+!%&":
        res = res.replace(etc, "")
    return res

def primary_fields(lst, debug=0):
    assert isinstance(lst, list), "List"
    first = sorted(
        set(sorted([simplex(ala) for ala in lst[:4] if len(ala) > 1]))
    )
    junk = '+'.join(first)
    hexs = hashlib.md5(bytes(junk, "ascii")).hexdigest()[:8]
    dprint(
        "primary_fields():", hexs, junk,
        debug=debug
    )
    return hexs, first

def calc_hexs2(astr:str) -> str:
    assert isinstance(astr, str), "String"
    res = hashlib.md5(bytes(astr, "utf-8")).hexdigest()[:-8]
    return res

def simpler_field(astr:str) -> str:
    """ Returns a simpler field heading """
    res = astr.replace(" ", "").replace("-", "")
    return res
