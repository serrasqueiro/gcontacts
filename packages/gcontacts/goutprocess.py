# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Dump output to individual filename-hashed files.

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring, consider-using-with

import hashlib
import gcontacts.csvpayload
from gcontacts.csvpayload import CPayload
from gcontacts.fields import CFields
from gcontacts.dprint import dprint

def process_outs(path, outdir, ccc, debug=0):
    # Organize output
    dct, dhex, shex = {}, {}, {}
    for idx, card in enumerate(ccc.cards, 1):
        hexs2 = calc_hexs2(card)
        lst = CPayload().line_wrap(card)
        hexs1, first = primary_fields(lst)
        dprint(
            f"# Debug: idx={idx} hexs1={hexs1}",
            first if first else "[NADA]", [] if first else lst,
            debug=debug,
        )
        assert len(lst) == len(CFields().fields), f"Card# {idx} ({first}): expected fields"
        dct[idx] = (hexs1, hexs2, '+'.join(first), lst)
        if hexs2 in dhex:
            dhex[hexs2].append(idx)
        else:
            dhex[hexs2] = [idx]
        if hexs1 in shex:
            if hexs2 not in shex[hexs1]:
                shex[hexs1].append(hexs2)
        else:
            shex[hexs1] = [hexs2]
    # Check duplicates
    for key, vals in dhex.items():
        if len(vals) <= 1:
            continue
        dprint(
            "# Absolute duplicate:", key, vals,
            dct[vals[0]][2],
            debug=debug,
        )
    # Check relative duplicates
    for key, vals in shex.items():
        if len(vals) <= 1:
            continue
        idx = dhex[vals[0]][0]
        dprint(
            "# Rel.", key, vals,
            dct[idx][2],
            debug=debug,
        )
    for key in sorted(dct):
        item = dct[key]
        hexs1, hexs2, first = item[:3]
        nums = shex[item[0]]
        #print(":::", key, item[:3], ">", len(nums), nums)
        assert nums, "!"
    return 0, ""

def primary_fields(lst):
    simplex = gcontacts.csvpayload.simplex
    first = list(set(sorted([simplex(ala) for ala in lst[:4] if len(ala) > 1])))
    junk = '+'.join(first)
    hexs = hashlib.md5(bytes(junk, "ascii")).hexdigest()[:8]
    return hexs, first

def calc_hexs2(astr:str) -> str:
    res = hashlib.md5(bytes(astr, "utf-8")).hexdigest()[:-8]
    return res
