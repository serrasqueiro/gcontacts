# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Simplifier -- for ASCII outputs

Author: Henrique Moreira
"""

from unidecode import unidecode

def simpler_words(obj):
    """ Returns the un-accented words from a string or a list of strings. """
    if isinstance(obj, str):
        return unidecode(obj)
    if not isinstance(obj, list):
        return "?"
    return [simpler_words(item) for item in obj]
