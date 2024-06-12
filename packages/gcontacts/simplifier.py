# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Simplifier -- for ASCII outputs

Author: Henrique Moreira
"""

from unidecode import unidecode

def simpler_words(obj):
    if isinstance(obj, str):
        return unidecode(obj)
    if not isinstance(obj, list):
        return "?"
    return [simpler_words(item) for item in obj]
