# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Dump output to individual filename-hashed files.

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring, too-many-locals

import os.path
import hashlib
import gcontacts.csvpayload
from gcontacts.csvpayload import CPayload
from gcontacts.fields import CFields
from gcontacts.dprint import dprint

C_SUFFIX = ".txt"

def process_outs(path, outdir, ccc, debug=0):
    # Organize output
    dct, dhex, shex = {}, {}, {}
    n_fields = CFields().num_fields()
    for idx, card in enumerate(ccc.cards, 1):
        hexs2 = calc_hexs2(card)
        lst = CPayload().line_wrap(card)
        hexs1, first = primary_fields(lst)
        dprint(
            f"# Debug: idx={idx} hexs1={hexs1}",
            first if first else "[NADA]", [] if first else lst,
            debug=debug,
        )
        assert len(lst) == n_fields, f"Card# {idx} ({first}): expected {n_fields} fields"
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
    # Marrying m_key: <short-hash>-nn-<24bit-hash>
    used = {}
    for key in sorted(dct):
        used[key] = ""	# Stores the m_key of messages
    for key, vals in shex.items():
        for sub_idx, ahex in enumerate(sorted(vals), 11 if len(vals) > 1 else 1):
            lst_idx = dhex[ahex]
            subid = f"{sub_idx:02}"
            m_key = f"{key}-{subid}-{ahex}"
            #print("m_key:", m_key, lst_idx)
            for duplicated, idx in enumerate(lst_idx):
                assert not used[idx], "There?"
                used[idx] = m_key + ("+" if duplicated else "")
    # Write individual card files
    for key, vals in used.items():
        if vals.endswith("+"):
            continue
        dump_card_file(os.path.join(outdir, vals + C_SUFFIX), dct[key][-1])
    # Inform of output consistency (all entries handled?)
    for key, m_key in used.items():
        if not m_key:
            return 4, f"Missing to address entry, index {key}"
    dump_index(
        os.path.join(outdir, "index.tsv"),
        os.path.join(outdir, "hindex.tsv"),
        (used, dct),
    )
    return 0, ""

def dump_card_file(outname:str, cont):
    """ Output a single card file """
    astr = ""
    for idx, entry in enumerate(cont, 1):
        s_num = f"{idx}: " if entry else f"{idx}."
        astr += f"{s_num}{entry}" + "\n"
    with open(outname, "wb") as fdout:
        fdout.write(bytes(astr, "utf-8"))
    return True

def dump_index(outname:str, hindex:str, tups):
    used, dct = tups
    lines = ["#card-idx\tm-key"]
    mydict = {}
    for key, val in used.items():
        unique = not val.endswith("+")
        first = dct[key][2]
        suffix = f" # {first}" if first and unique else ""
        lines.append(f"{key}\t{val}{suffix}")
        if not first or not unique:
            continue
        if first[0].isalpha():
            mydict[first] = val
        else:
            mydict["@_" + first] = val
    astr = '\n'.join(lines) + '\n'
    with open(outname, "wb") as fdout:
        fdout.write(bytes(astr, "ascii"))
    # Build hindex tsv output:
    lines = ["#m-key\tup-name"]
    for key in sorted(mydict):
        val = mydict[key]
        new_key = key.replace("@_", "").replace("+", " ")
        lines.append(f"{val}\t{new_key}")
    astr = '\n'.join(lines) + '\n'
    with open(hindex, "wb") as fdout:
        fdout.write(bytes(astr, "ascii"))
    return True

def primary_fields(lst):
    simplex = gcontacts.csvpayload.simplex
    first = list(set(sorted([simplex(ala) for ala in lst[:4] if len(ala) > 1])))
    junk = '+'.join(first)
    hexs = hashlib.md5(bytes(junk, "ascii")).hexdigest()[:8]
    return hexs, first

def calc_hexs2(astr:str) -> str:
    res = hashlib.md5(bytes(astr, "utf-8")).hexdigest()[:-8]
    return res
